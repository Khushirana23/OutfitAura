from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.app.database import get_database

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])

class NewsletterSubscribe(BaseModel):
    email: EmailStr

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe_newsletter(
    req: NewsletterSubscribe,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Subscribe email to the 'Stay in the Aura' luxury fashion drop list."""
    email_clean = req.email.lower()
    
    existing = await db.newsletter.find_one({"email": email_clean})
    if existing:
        return {
            "status": "already_subscribed",
            "message": "You are already subscribed to the OutfitAura private drops list.",
            "discount_code": "AURA10"
        }

    await db.newsletter.insert_one({
        "email": email_clean,
        "subscribed_at": datetime.now(timezone.utc),
        "is_active": True
    })

    return {
        "status": "success",
        "message": "Welcome to the Aura circle. Enjoy 10% off your first purchase.",
        "discount_code": "AURA10"
    }
