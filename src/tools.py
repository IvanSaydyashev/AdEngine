import json
from typing import List

import redis
from fastapi import HTTPException
from sqlalchemy.dialects.oracle.dictionary import dictionary_meta

from src.advertiser.models import MLScoreModel


def except_null(dictionary):
    return {k: v for k, v in dictionary.items() if v is not None}


def paginate(items, page, per_page):
    try:
        if per_page is None:
            per_page = len(items)
        if page is None or page < 1:
            page = 1
    except:
        return items
    return items[(page - 1) * per_page: page * per_page]

def instrumented_attribute_to_json(attr):
    if isinstance(attr, str):  # Если уже строка JSON
        try:
            return json.loads(attr)
        except json.JSONDecodeError:
            return {}  # Возвращаем пустой словарь при ошибке парсинга
    elif isinstance(attr, dict):  # Если уже словарь
        return attr
    elif hasattr(attr, "expression"):  # Если это InstrumentedAttribute
        return json.loads(attr.expression) if isinstance(attr.expression, str) else {}
    return {}  # Если формат неизвестен, возвращаем пустой словарь

def read_target_dict(targeting_data) -> dict:
    dictionary = instrumented_attribute_to_json(targeting_data)
    return {
        "gender": dictionary.get('gender', 'ALL'),
        "min_age": dictionary.get("min_age", 0),
        "max_age": dictionary.get("max_age", 100),
        "location": dictionary.get("location", ""),
    }

