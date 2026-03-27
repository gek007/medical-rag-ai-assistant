from fastapi import APIRouter, Depends, Form, HTTPException

from auth import authenticate
from config.logger import get_logger

from .chat_query import answer_question

logger = get_logger("chat.routes")
logger.info("chat.routes module initialized")

router = APIRouter()


@router.post("/chat")
async def chat(user=Depends(authenticate), question: str = Form(...)):
    try:
        response = await answer_question(question, user["role"])
        return response
    except Exception as e:
        logger.error("Error in chat | error=%s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
