import logging_config  # Must be first
import logging
from fastapi import FastAPI, HTTPException, Query
from config import LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL
import requests

app = FastAPI(title="AI-SystemAnalitic API", version="1.0.0")

logger = logging.getLogger(__name__)

SAVED_PROMPT = "Ты инденер данных в финтехе, посоветуй в каких компонентах истемы надо сделать операции и какие, для того чтобы дать польователю то что он хочет?"

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
    
    result = {
        "is_enough": True,  # As per spec, always true for this service
        "response": llm_response
    }
    logger.info("Analytics prepared", extra=result)
    return result

@app.get("/health")
async def health():
    return {"status": "healthy"}