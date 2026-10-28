from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.app.database import get_database
from backend.app.models.product import ProductModel
from backend.app.models.user import UserResponse
from backend.app.utils.auth import get_current_user

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.get("", response_model=List[ProductModel])
async def get_user_wishlist(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Retrieve full product details of saved wishlist items."""
    user_doc = await db.users.find_one({"id": current_user.id})
    product_ids = user_doc.get("wishlist", []) if user_doc else []
    
    if not product_ids:
        return []

    cursor = db.products.find({"id": {"$in": product_ids}})
    docs = await cursor.to_list(length=100)
    return [ProductModel(**{**doc, "id": str(doc.get("id") or doc.get("_id"))}) for doc in docs]

@router.post("/{product_id}")
async def toggle_wishlist_item(
    product_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Toggle a product in the user's wishlist (Add / Remove)."""
    prod = await db.products.find_one({"id": product_id})
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found.")

    user_doc = await db.users.find_one({"id": current_user.id})
    wishlist = user_doc.get("wishlist", []) if user_doc else []

    if product_id in wishlist:
        wishlist.remove(product_id)
        action = "removed"
    else:
        wishlist.append(product_id)
        action = "added"

    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"wishlist": wishlist}}
    )

    return {
        "status": "success",
        "action": action,
        "product_id": product_id,
        "wishlist_count": len(wishlist),
        "wishlist": wishlist
    }
