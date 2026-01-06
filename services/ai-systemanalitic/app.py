import logging_config  # Must be first
import logging
import json
from fastapi import FastAPI, HTTPException, Query
from config import LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL
import requests

app = FastAPI(title="AI-SystemAnalitic API", version="1.0.0")

logger = logging.getLogger(__name__)

SAVED_PROMPT = """
    Ты инженер данных в финтехе, посоветуй в каких компонентах стемы надо 
    сделать операции и какие, для того чтобы дать пользователю то что он хочет?
    Если информации достаточно - верни is_enough - true а в атрибут reasoning запиши 
    список действий и мест для их выполнения, ссылок на документацию или репозитории которые 
    для этого понадобятся
    Если информации не достаточно или нет уверенности в конкретном запросе  верни is_enough - true 
    а в атрибут reasoning сформулируй уточняюащий вопрос с объяснением почему ты его задаешь.
    Верни ответ строго в json формате:
    {
        "is_enough": boolean,
        "reasoning": string
    }
    """

@app.get("/prepare-analititcs")
async def prepare_analitics(
    preparedcontext: str = Query(...),
    request: str = Query(...)
):
    logger.info("Received prepare-analititcs", extra={"preparedcontext": preparedcontext, "request": request})
    
    prompt = f"{SAVED_PROMPT} Контекст: {preparedcontext}, Запрос: {request}"
    
    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = requests.post(
            LLM_ENDPOINT,
            headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
            json={"model": LLM_MODEL, "messages": messages}
        )
        response.raise_for_status()
        llm_data = response.json()
        llm_response = llm_data["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logger.error("Error calling LLM", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")
    except KeyError:
        logger.error("Unexpected LLM response format", extra={"response": llm_data})
        raise HTTPException(status_code=500, detail="Internal server error")
    
    try:
        parsed = json.loads(llm_response)
        is_enough = parsed["is_enough"]
        reasoning = parsed["reasoning"]
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Failed to parse LLM response", extra={"error": str(e), "response": llm_response})
        raise HTTPException(status_code=500, detail="Internal server error")

    result = {
        "is_enough": is_enough,
        "reasoning": reasoning
    }
    logger.info("Analytics prepared", extra=result)
    return result

@app.get("/health")
async def health():
    return {"status": "healthy"}