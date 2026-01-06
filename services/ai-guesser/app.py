import logging_config  # Must be first
import logging
from fastapi import FastAPI, HTTPException, Query
from config import LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL
import requests

app = FastAPI(title="AI-Guesser API", version="1.0.0")

logger = logging.getLogger(__name__)

SAVED_PROMPT = "Ты системный аналитик в финтехе, определи запрос пользователя достаточне для того чтобы понять в какой предметной области находится то что ему интересно?"

@app.get("/get-context")
async def get_context(
    username: str = Query(...),
    department: str = Query(...),  # Note: in spec it's department: userdepartment, but name is department
    position: str = Query(...),
    request: str = Query(...)
):
    logger.info("Received get-context", extra={"username": username, "department": department, "position": position, "request": request})
    
    prompt = f"{SAVED_PROMPT} Пользователь: {username}, Департамент: {department}, Должность: {position}, Запрос: {request}"
    
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
    
    # For simplicity, assume if "достаточно" in response, is_enough True, else False
    is_enough = "достаточно" in llm_response.lower()
    
    result = {
        "is_enough": is_enough,
        "response": llm_response
    }
    logger.info("Context determined", extra=result)
    return result

@app.get("/health")
async def health():
    return {"status": "healthy"}