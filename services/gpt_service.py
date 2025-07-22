import openai
import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class GPTService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def get_response(
        self, 
        user_message: str, 
        session_id: str, 
        db: AsyncSession,
        model: str = "gpt-4o"
    ) -> str:
        try:
            # Get conversation history
            history = await self._get_conversation_history(session_id, db)
            
            # TODO: Get uploaded file data context
            file_context = await self._get_file_context(db)
            
            # Build messages for GPT
            messages = [
                {
                    "role": "system", 
                    "content": f"""You are an AI assistant that helps with data analysis and general tasks. 
                    
                    Available data context:
                    {file_context}
                    
                    Please provide helpful and accurate responses based on the user's questions and available data."""
                }
            ]
            
            # Add conversation history
            for msg in history:
                role = "user" if msg["speaker"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["message"]})
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def _get_conversation_history(self, session_id: str, db: AsyncSession, limit: int = 10):
        """Get recent conversation history for context"""
        try:
            result = await db.execute(
                text("""
                    SELECT speaker, message 
                    FROM chat_logs 
                    WHERE session_id = :session_id 
                    ORDER BY created_at DESC 
                    LIMIT :limit
                """),
                {"session_id": session_id, "limit": limit}
            )
            
            rows = result.fetchall()
            # Reverse to get chronological order
            return [{"speaker": row.speaker, "message": row.message} for row in reversed(rows)]
            
        except Exception:
            return []
    
    async def _get_file_context(self, db: AsyncSession) -> str:
        """Get context from uploaded files - TODO: implement proper file storage and retrieval"""
        # TODO: Implement file data retrieval from database
        return "No file data currently available. This feature will be implemented to include uploaded CSV data context."