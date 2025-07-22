from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
import uuid

from db.session import get_db
from services.gpt_service import GPTService
from models.chat_log import ChatLog
from models.assistant import Assistant

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    input_type: str = "text"  # "text", "voice", "file"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    assistant_id: int

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        # Get default assistant (TODO: make configurable)
        assistant = await db.get(Assistant, 1)
        if not assistant:
            raise HTTPException(status_code=404, detail="Assistant not found")
        
        # Log user message
        user_log = ChatLog(
            session_id=session_id,
            user_id=message.user_id,
            speaker="user",
            assistant_id=assistant.id,
            input_type=message.input_type,
            message=message.message
        )
        db.add(user_log)
        
        # Get GPT response
        gpt_service = GPTService()
        response = await gpt_service.get_response(message.message, session_id, db)
        
        # Log assistant response
        assistant_log = ChatLog(
            session_id=session_id,
            user_id=message.user_id,
            speaker="assistant",
            assistant_id=assistant.id,
            input_type="text",
            message=response
        )
        db.add(assistant_log)
        
        await db.commit()
        
        return ChatResponse(
            response=response,
            session_id=session_id,
            assistant_id=assistant.id
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            "SELECT * FROM chat_logs WHERE session_id = :session_id ORDER BY created_at",
            {"session_id": session_id}
        )
        logs = result.fetchall()
        
        messages = [
            {
                "speaker": log.speaker,
                "message": log.message,
                "input_type": log.input_type,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=messages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))