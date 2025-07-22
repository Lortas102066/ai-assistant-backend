from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from db.session import get_db
from services.whisper_service import WhisperService
from services.tts_service import TTSService

router = APIRouter()

class TranscriptionResponse(BaseModel):
    text: str
    success: bool

class TTSRequest(BaseModel):
    text: str
    language: str = "en"

@router.post("/speech/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Validate file type
        allowed_types = ["audio/wav", "audio/mp3", "audio/mpeg", "audio/webm"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported audio format. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read audio content
        audio_content = await file.read()
        
        # Transcribe using Whisper
        whisper_service = WhisperService()
        text = await whisper_service.transcribe(audio_content, file.filename)
        
        return TranscriptionResponse(
            text=text,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/speech/synthesize")
async def synthesize_speech(
    request: TTSRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Generate speech using Google TTS
        tts_service = TTSService()
        audio_content = await tts_service.synthesize(request.text, request.language)
        
        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")