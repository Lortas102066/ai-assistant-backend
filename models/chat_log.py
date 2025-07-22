from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class ChatLog(BaseModel):
    __tablename__ = "chat_logs"
    
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), nullable=True)  # Optional for now
    speaker = Column(String(20), nullable=False)  # "user" or "assistant"
    assistant_id = Column(Integer, ForeignKey("assistants.id"), nullable=True)
    input_type = Column(String(20), nullable=False)  # "text", "voice", "file"
    message = Column(Text, nullable=False)
    
    # Relationship
    assistant = relationship("Assistant", backref="chat_logs")