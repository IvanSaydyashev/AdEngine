import json

from fastapi import HTTPException
from together import Together
from src.config import settings

API_KEY = settings.LLM_API_KEY
client = Together(api_key=API_KEY)


def get_data(data: dict) -> str:
    try:
        data_str = json.dumps(data, ensure_ascii=False)
        return data_str
    except:
        raise HTTPException(status_code=400, detail="JSON is not valid")


def request_llm(prompt: str, data: str) -> str:
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
        messages=[{"role": "system", "content": prompt},
                  {"role": "system",
                   "content": data}],
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=True
    )

    llm_answer = ''

    for token in response:
        if hasattr(token, 'choices'):
            llm_answer += token.choices[0].delta.content
    return llm_answer


def request_validation_llm(data):
    data_str = get_data(data)
    prompt = (
        '"Проверь рекламный текст на наличие матерных или оскорбительных слов.'
        ' Если текст содержит такие слова, верни только: {\"status\": \"reject\", \"reason\": \"{{reason}}\"}. Если все в порядке, верни только:'
        ' {\"status\": \"accept\"}. Вот текст: \"{{ad_text}}\"."}'
    )
    return request_llm(prompt, data_str)


def request_generation_llm(data):
    data_str = get_data(data)
    prompt = (
        '"Сгенерируй рекламный текст для следующего объявления,'
        ' основываясь на его названии, таргетинге и названии рекламодателя. Используй креативный подход, чтобы привлечь внимание'
        ' пользователей. Верни только сгенерированный текст без дополнительных пояснений.'
        ' верни только {{ad_text}}'
    )
    return request_llm(prompt, data_str)
