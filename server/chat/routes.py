from fastapi import APIRouter, Depends, HTTPException

from auth import authenticate
from config.logger import get_logger

from .chat_query import answer_question
from .models import ChatRequest

logger = get_logger("chat.routes")
logger.info("chat.routes module initialized")

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest, user=Depends(authenticate)):
    logger.info("Chat request | user=%s question=%s", user["username"], request.question)

    try:
        response = await answer_question(request.question, user["role"])
        return response
    except Exception as e:
        logger.error("Error in chat | error=%s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
