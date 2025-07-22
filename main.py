from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from routers import chat, upload, speech
from db.session import engine
from models.base import Base

load_dotenv()

app = FastAPI(
    title="AI Assistant API",
    description="AI Assistant backend with voice, chat, and file upload capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize default data
    from db.init_data import init_assistant_data
    await init_assistant_data()

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(speech.router, prefix="/api", tags=["speech"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Assistant API is running"}

@app.get("/")
async def root():
    return {"message": "Welcome to AI Assistant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)