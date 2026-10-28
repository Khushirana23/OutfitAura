from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.app.database import db_manager, get_database
from backend.app.config import settings

router = APIRouter(prefix="/health", tags=["System Health"])

@router.get("")
async def health_check(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Health check endpoint to test API status and MongoDB Atlas connectivity."""
    db_health = await db_manager.check_health()
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_health
    }
