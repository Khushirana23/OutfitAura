import uuid
import random
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.app.database import get_database
from backend.app.models.order import OrderCreate, OrderResponse, OrderItem
from backend.app.models.user import UserResponse
from backend.app.utils.auth import get_current_user, get_current_user_optional

router = APIRouter(prefix="/orders", tags=["Orders & Checkout"])

def generate_order_number() -> str:
    now = datetime.now(timezone.utc)
    rand = random.randint(1000, 9999)
    return f"OA-{now.strftime('%y%m%d')}-{rand}"

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Place a new e-commerce order."""
    if not order_in.items:
        raise HTTPException(status_code=400, detail="Cannot create an empty order.")

    subtotal = sum(it.subtotal for it in order_in.items)
    shipping_fee = 0.0 if subtotal >= 150 else 15.0
    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + shipping_fee + tax, 2)

    order_id = f"ord_{uuid.uuid4().hex[:12]}"
    order_num = generate_order_number()

    order_doc = {
        "id": order_id,
        "user_id": current_user.id if current_user else None,
        "order_number": order_num,
        "items": [it.dict() for it in order_in.items],
        "shipping_address": order_in.shipping_address.dict(),
        "subtotal": round(subtotal, 2),
        "shipping_fee": round(shipping_fee, 2),
        "tax": tax,
        "total": total,
        "payment_method": order_in.payment_method,
        "payment_status": "paid",
        "order_status": "processing",
        "notes": order_in.notes,
        "created_at": datetime.now(timezone.utc)
    }

    await db.orders.insert_one(order_doc)

    # If user has a cart, clear it after checkout
    if current_user:
        await db.cart.update_one({"user_id": current_user.id}, {"$set": {"items": []}})

    # Decrement inventory stock
    for item in order_in.items:
        await db.products.update_one(
            {"id": item.product_id},
            {"$inc": {"stock": -item.quantity}}
        )

    return OrderResponse(**order_doc)

@router.get("", response_model=List[OrderResponse])
async def list_user_orders(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """List purchase history for the authenticated user."""
    cursor = db.orders.find({"user_id": current_user.id}).sort("created_at", -1)
    docs = await cursor.to_list(length=50)
    return [OrderResponse(**{**doc, "id": str(doc.get("id") or doc.get("_id"))}) for doc in docs]

@router.get("/{id_or_number}", response_model=OrderResponse)
async def get_order(
    id_or_number: str,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Retrieve order details by order ID or Order Number."""
    doc = await db.orders.find_one({"$or": [{"id": id_or_number}, {"order_number": id_or_number}]})
    if not doc:
        raise HTTPException(status_code=404, detail="Order not found.")

    # If authenticated, ensure ownership or admin
    if current_user and current_user.role != "admin" and doc.get("user_id") and doc.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to view this order.")

    doc["id"] = str(doc.get("id") or doc.get("_id"))
    return OrderResponse(**doc)
