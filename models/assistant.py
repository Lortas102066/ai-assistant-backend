from sqlalchemy import Column, String
from .base import BaseModel

class Assistant(BaseModel):
    __tablename__ = "assistants"
    
    name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # e.g., "openai"
    model = Column(String(100), nullable=False)    # e.g., "gpt-4o"