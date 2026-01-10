import logging_config  # Must be first
import logging
import json
from fastapi import FastAPI, HTTPException, Query
from config import LLM_API_KEY, LLM_ENDPOINT, LLM_MODEL
import requests

app = FastAPI(title="AI-SystemAnalitic API", version="1.0.0")

logger = logging.getLogger(__name__)

INVESTIGATIVE_PROMPT = """
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

DETERMINATE_ACTION_PROMT = """
    Ты системный аналитик в финтехе, на основе описания определи какое из трех действий нужно предпринять:
    'develop' - описание предпологает разработку нового функционала
    'consult' - все что необходимо пользователю уже есть, необходимо проконсульитровать пользователя как из этого получить то что ему нужно
    'escalate' - не понятно что нужно пользователю или же то что ему требуется не может быть реализовано
    Верни ответ строго в json формате:
    {
        "action": string,
        "reasoning": string
    }
    где в action строго оно из трез слов: 'develop', 'consult', 'escalate'
    а в reasoning объясни почему ты выбрал именно это решение
    """

@app.get("/prepare-analititcs")
async def prepare_analitics(
    preparedcontext: str = Query(...),
    request: str = Query(...)
):
    logger.info("Received prepare-analititcs", extra={"preparedcontext": preparedcontext, "request": request})
    
    investigative_prompt = f"{INVESTIGATIVE_PROMPT} Контекст: {preparedcontext}, Запрос: {request}"
    
    investigative_messages = [{"role": "user", "content": investigative_prompt}]
    
    try:
        investigative_response = requests.post(
            LLM_ENDPOINT,
            headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
            json={"model": LLM_MODEL, "messages": investigative_messages}
        )
        investigative_response.raise_for_status()
        llm_investigative_data = investigative_response.json()
        llm_investigative_response = llm_investigative_data["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logger.error("Error calling LLM", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")
    except KeyError:
        logger.error("Unexpected LLM response format", extra={"response": llm_investigative_data})
        raise HTTPException(status_code=500, detail="Internal server error")
    
    try:
        parsed = json.loads(llm_investigative_response)
        is_enough = parsed["is_enough"]
        investigative_reasoning = parsed["reasoning"]
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Failed to parse LLM investigative_response", extra={"error": str(e), "response": llm_investigative_response})
        raise HTTPException(status_code=500, detail="Internal server error")
    
    if is_enough:
        determinate_action_prompt = f"{DETERMINATE_ACTION_PROMT} Контекст: {preparedcontext}, Запрос: {request} По этому запросу определено что: {investigative_reasoning} "
        
        determinate_action_messages = [{"role": "user", "content": determinate_action_prompt}]

        try:
            determinate_action_response = requests.post(
                LLM_ENDPOINT,
                headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
                json={"model": LLM_MODEL, "messages": determinate_action_messages}
            )
            determinate_action_response.raise_for_status()
            llm_determinate_action_data = determinate_action_response.json()
            llm_determinate_action_response = llm_determinate_action_data["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            logger.error("Error calling LLM", extra={"error": str(e)})
            raise HTTPException(status_code=500, detail="Internal server error")
        except KeyError:
            logger.error("Unexpected LLM determinate_action_response format", extra={"response": llm_determinate_action_data})
            raise HTTPException(status_code=500, detail="Internal server error")
        
        try:
            determinate_action_parsed = json.loads(llm_determinate_action_response)
            action = determinate_action_parsed["action"]
            determinate_action_reasoning = determinate_action_parsed["reasoning"]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to parse LLM determinate_action_response", extra={"error": str(e), "response": llm_determinate_action_response})
            raise HTTPException(status_code=500, detail="Internal server error")

    result = {
        "is_enough": is_enough,
        "investigative_reasoning": investigative_reasoning,
        "action": action or "",
        "determinate_action_reasoning": determinate_action_reasoning or ""
    }
    logger.info("Analytics prepared", extra=result)
    return result

@app.get("/health")
async def health():
    return {"status": "healthy"}