from fastapi import APIRouter, HTTPException, Depends

from src.llm_api.schemas import *
from src.llm_api.services import *

router = APIRouter()


@router.post("/llm-action/validate", tags=["LLM-Action"], name="Модерация текстов рекламных кампаний",
             description="Эндпоинт для модерации рекламных текстов с использованием модели для проверки соответствия"
                         " рекламного контента. Принимает запрос с текстом рекламы и возвращает результат в формате JSON,"
                         " подтверждающий, был ли текст принят или отклонён."
                         " В случае ошибки при обработке ответа от модели или неверного формата данных, возвращается ошибка 400."
             )
async def llm_validate(request_data: LLMValidateRequestSchema):
    # TESTING OFF
    ###################################
    data = request_data.model_dump()
    data_str = get_data(data)

    llm_response = request_validation_llm(data_str)
    return json.loads(llm_response)
    ###################################
    # return {"status": "accept"}


@router.post("/llm-action/generate", tags=["LLM-Action"], name="Генерация рекламных текстов",
             description="Эндпоинт для генерации рекламных текстов с использованием модели."
                         " Принимает запрос с параметрами таргетинга и названием рекламы, а затем генерирует рекламный текст,"
                         " соответствующий заданным условиям."
                         " В случае ошибки при обработке данных или ответа от модели возвращается ошибка 400."
             )
def llm_generate(request_data: LLMGenerateRequestSchema):
    # TESTING OFF
    ###################################
    data = request_data.model_dump()
    data_str = get_data(data)
    llm_response = request_generation_llm(data_str)
    return llm_response
    ###################################
    # return {"ad_text": "ad_text"}
