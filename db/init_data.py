"""
Initialize database with default data
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import async_session
from models.assistant import Assistant

async def init_assistant_data():
    """Create default assistant if it doesn't exist"""
    async with async_session() as db:
        try:
            # Check if assistant already exists
            result = await db.execute(select(Assistant).where(Assistant.id == 1))
            existing = result.scalar_one_or_none()
            
            if not existing:
                assistant = Assistant(
                    name="GPT-4o Assistant",
                    provider="openai",
                    model="gpt-4o"
                )
                db.add(assistant)
                await db.commit()
                print("✅ Default assistant created successfully")
            else:
                print("ℹ️ Default assistant already exists")
                
        except Exception as e:
            print(f"❌ Error initializing assistant data: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(init_assistant_data())