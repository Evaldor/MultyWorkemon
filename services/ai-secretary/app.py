import logging_config  # Must be first
import logging
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, RequestHistory
from config import DATABASE_URL, AI_GUESSER_URL, AI_SYSTEMANALITIC_URL
import requests
from typing import Optional

app = FastAPI(title="AI-Secretary API", version="1.0.0")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)  # For simplicity, create tables

logger = logging.getLogger(__name__)

@app.get("/analyze-request")
async def analyze_request(
    channel: str = Query(..., enum=["email", "tg", "direct"]),
    username: str = Query(...),
    request: str = Query(...),
    userdepartment: str = Query(...),
    userposition: str = Query(...)
):
    logger.info("Received analyze-request", extra={"channel": channel, "username": username, "request": request})
    
    # Save request to history
    db = SessionLocal()
    history = RequestHistory(channel=channel, username=username, request_text=request)
    db.add(history)
    db.commit()
    db.refresh(history)
    
    # Call AI-Guesser
    guesser_params = {
        "username": username,
        "department": userdepartment or "",
        "position": userposition or "",
        "request": request
    }
    try:
        response = requests.get(f"{AI_GUESSER_URL}/get-context", params=guesser_params)
        response.raise_for_status()
        context_data = response.json()
    except requests.RequestException as e:
        logger.error("Error calling AI-Guesser", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")
    
    if context_data.get("is_enough"):
        # Call AI-SystemAnalitic
        analitic_params = {
            "preparedcontext": context_data["response"],
            "request": request
        }
        try:
            response = requests.get(f"{AI_SYSTEMANALITIC_URL}/prepare-analititcs", params=analitic_params)
            response.raise_for_status()
            analitic_data = response.json()
        except requests.RequestException as e:
            logger.error("Error calling AI-SystemAnalitic", extra={"error": str(e)})
            raise HTTPException(status_code=500, detail="Internal server error")
        
        final_response = analitic_data["response"]
        action = "ответить сообщением"  # Assuming based on context
        question = ""
    else:
        final_response = context_data["response"]
        action = "уточнить"
        question = context_data["response"]
    
    # Update history with response
    history.response = final_response
    db.commit()
    db.close()
    
    result = {
        "is_enough": context_data.get("is_enough", False),
        "request": request,
        "action": action,
        "question": question,
        "response": final_response
    }
    logger.info("Analysis complete", extra=result)
    return result

@app.get("/health")
async def health():
    return {"status": "healthy"}