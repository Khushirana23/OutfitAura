from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    comment: str
    size_purchased: Optional[str] = None
    color_purchased: Optional[str] = None

class ReviewResponse(BaseModel):
    id: str
    product_id: str
    user_id: str
    user_name: str
    rating: int
    title: Optional[str] = None
    comment: str
    size_purchased: Optional[str] = None
    color_purchased: Optional[str] = None
    created_at: datetime
