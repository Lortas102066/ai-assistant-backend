import openai
import os
import tempfile
import aiofiles
from typing import BinaryIO

class WhisperService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def transcribe(self, audio_content: bytes, filename: str) -> str:
        """
        Transcribe audio content using OpenAI Whisper API
        """
        try:
            # Create temporary file for audio content
            with tempfile.NamedTemporaryFile(delete=False, suffix=self._get_file_extension(filename)) as tmp_file:
                tmp_file.write(audio_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Open file and send to Whisper API
                with open(tmp_file_path, "rb") as audio_file:
                    response = await self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                
                return response.strip()
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            raise Exception(f"Whisper transcription failed: {str(e)}")
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension, default to .wav if not found"""
        if '.' in filename:
            return '.' + filename.split('.')[-1]
        return '.wav'