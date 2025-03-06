import redis
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict, List, Type

from src.advertiser.models import *
from src.campaign.models import *
from src.client.models import *
from src.stats.models import *


# ========================
# FILTERING AND METRICS
# ========================

def is_targeting_violated(client: Type[ClientModel], campaign: Type[CampaignModel]) -> bool:
    targeting = campaign.targeting
    if targeting is None:
        return False

    # Проверка пола
    if targeting.get('gender', 'ALL') != 'ALL' and targeting['gender'] != client.gender:
        return True

    # Проверка возраста
    min_age = targeting.get('min_age', 0)
    max_age = targeting.get('max_age', 1000)
    if not (min_age <= client.age <= max_age):
        return True

    # Проверка локации
    if targeting.get('location') and targeting['location'] != client.location:
        return True

    return False


def calculate_campaign_metrics(
        campaign: Type[CampaignModel],
        ml_score: float,
        total_views: int,
        is_targeting_violated: bool
) -> Dict:
    penalties = 0.0

    if campaign.impressions_limit > 0:
        excess_views = max(0, total_views - campaign.impressions_limit)
        excess_percentage = (excess_views / campaign.impressions_limit) * 100
        penalties += (excess_percentage // 5) * 0.05  # -5% за каждые 5%

    if is_targeting_violated:
        penalties += 0.10  # -10%

    base_profit = (campaign.cost_per_impression + ml_score * campaign.cost_per_click)
    adjusted_profit = base_profit * (1 - min(penalties, 1.0))  # Максимальный штраф 100%

    fulfillment = min(
        total_views / campaign.impressions_limit if campaign.impressions_limit > 0 else 1.0,
        2.0
    )

    return {
        'expected_profit': adjusted_profit,
        'relevance': ml_score * 100,
        'fulfillment': fulfillment,
        'campaign': campaign,
        'penalties': penalties
    }


# ========================
# CORE LOGIC
# ========================

def select_best_campaign(
        db: Session,
        ml_scores: List[MLScoreModel],
        client: Type[ClientModel],
        current_date: int):
    active_campaigns = db.query(CampaignModel).filter(
        CampaignModel.start_date <= current_date,
        CampaignModel.end_date >= current_date,
    ).all()

    ml_score_map = {ml.advertiser_id: ml.score / 100 for ml in ml_scores}

    ranked_campaigns = []
    for campaign in active_campaigns:
        total_views = db.query(func.sum(DailyStatsModel.impressions_count)).filter(
            DailyStatsModel.campaign_id == campaign.campaign_id
        ).scalar() or 0

        is_violated = is_targeting_violated(client, campaign)

        metrics = calculate_campaign_metrics(
            campaign=campaign,
            ml_score=ml_score_map.get(campaign.advertiser_id, 0),
            total_views=total_views,
            is_targeting_violated=is_violated
        )
        if metrics['penalties'] < 1.0:
            ranked_campaigns.append(metrics)

    if ranked_campaigns:
        weights = {'profit': 0.5, 'relevance': 0.25, 'fulfillment': 0.15}
        ranked_campaigns = normalize_metrics(ranked_campaigns, weights)

    return ranked_campaigns[0]['campaign'] if ranked_campaigns else None


def normalize_metrics(
        campaign_metrics: List[Dict],
        weights: Dict[str, float]
) -> List[Dict]:
    profits = [m['expected_profit'] for m in campaign_metrics]
    fulfillments = [m['fulfillment'] for m in campaign_metrics]

    min_max = {
        'profit': (min(profits), max(profits)),
        'relevance': (0, 100),
        'fulfillment': (min(fulfillments), max(fulfillments))
    }

    for metric in campaign_metrics:
        profit_range = min_max['profit'][1] - min_max['profit'][0]
        metric['norm_profit'] = (metric['expected_profit'] - min_max['profit'][
            0]) / profit_range if profit_range > 0 else 0.5

        metric['norm_relevance'] = metric['relevance'] / 100

        fulfillment_range = min_max['fulfillment'][1] - min_max['fulfillment'][0]
        metric['norm_fulfillment'] = (metric['fulfillment'] - min_max['fulfillment'][
            0]) / fulfillment_range if fulfillment_range > 0 else 0.5

        metric['composite_score'] = (
                weights['profit'] * metric['norm_profit'] +
                weights['relevance'] * metric['norm_relevance'] +
                weights['fulfillment'] * metric['norm_fulfillment']
        )

    return sorted(campaign_metrics, key=lambda x: x['composite_score'], reverse=True)


class Action(Enum):
    VIEW = "VIEW"
    CLICK = "CLICK"


def update_campaign_stats(
        action: Action,
        today: int,
        db: Session,
        campaign: Type[CampaignModel],
        cost_per_impression: float,
        cost_per_click: float,
) -> None:
    daily_stat = db.query(DailyStatsModel).filter(
        DailyStatsModel.campaign_id == campaign.campaign_id,
        DailyStatsModel.day == today
    ).first()

    if action == Action.VIEW:
        if daily_stat:
            daily_stat.impressions_count += 1
            daily_stat.spent_impressions += cost_per_impression
        else:
            db.add(DailyStatsModel(
                campaign_id=campaign.campaign_id,
                day=today,
                impressions_count=1,
                clicks_count=0,
                spent_impressions=cost_per_impression,
                spent_clicks=0
            ))
    elif action == Action.CLICK:
        if daily_stat:
            daily_stat.clicks_count += 1
            daily_stat.spent_clicks += cost_per_click
        else:
            db.add(DailyStatsModel(
                campaign_id=campaign.campaign_id,
                day=today,
                impressions_count=0,
                clicks_count=1,
                spent_impressions=0,
                spent_clicks=cost_per_click
            ))

    db.commit()
