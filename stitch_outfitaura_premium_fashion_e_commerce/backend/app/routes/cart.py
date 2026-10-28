import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Header, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.app.database import get_database
from backend.app.models.cart import (
    AddToCartRequest, 
    UpdateCartRequest, 
    CartResponse, 
    CartItem
)
from backend.app.models.product import ProductModel
from backend.app.models.user import UserResponse
from backend.app.utils.auth import get_current_user_optional

router = APIRouter(prefix="/cart", tags=["Shopping Bag"])

def calculate_cart_totals(items: List[CartItem]) -> dict:
    subtotal = sum(item.total_price for item in items)
    shipping_fee = 0.0 if subtotal >= 150 or subtotal == 0 else 15.0
    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + shipping_fee + tax, 2)
    total_items = sum(item.quantity for item in items)
    return {
        "subtotal": round(subtotal, 2),
        "shipping_fee": round(shipping_fee, 2),
        "tax": tax,
        "total": total,
        "total_items": total_items
    }

async def get_cart_identifier(current_user: Optional[UserResponse], x_session_id: Optional[str]) -> dict:
    if current_user:
        return {"user_id": current_user.id}
    if x_session_id:
        return {"session_id": x_session_id}
    # Default fallback
    return {"session_id": "guest_default"}

@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Retrieve shopping bag items and computed totals."""
    query = await get_cart_identifier(current_user, x_session_id)
    cart_doc = await db.cart.find_one(query)
    
    if not cart_doc or "items" not in cart_doc:
        return CartResponse(
            user_id=current_user.id if current_user else None,
            items=[],
            subtotal=0.0,
            shipping_fee=0.0,
            tax=0.0,
            total=0.0,
            total_items=0
        )

    cart_items = []
    for item in cart_doc.get("items", []):
        prod_doc = await db.products.find_one({"id": item["product_id"]})
        product_model = None
        unit_price = item.get("unit_price", 0.0)
        if prod_doc:
            prod_doc["id"] = str(prod_doc.get("id") or prod_doc.get("_id"))
            product_model = ProductModel(**prod_doc)
            unit_price = product_model.price

        total_price = round(unit_price * item["quantity"], 2)
        cart_items.append(CartItem(
            id=item["id"],
            product_id=item["product_id"],
            size=item["size"],
            color=item["color"],
            quantity=item["quantity"],
            unit_price=unit_price,
            total_price=total_price,
            product=product_model
        ))

    totals = calculate_cart_totals(cart_items)
    return CartResponse(
        user_id=current_user.id if current_user else None,
        items=cart_items,
        **totals
    )

@router.post("/items", response_model=CartResponse)
async def add_item_to_cart(
    req: AddToCartRequest,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Add a fashion garment to the shopping bag."""
    prod = await db.products.find_one({"id": req.product_id})
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found.")

    query = await get_cart_identifier(current_user, x_session_id)
    cart_doc = await db.cart.find_one(query)
    
    items = cart_doc.get("items", []) if cart_doc else []
    
    # Check if item with exact product, size, and color already exists
    matched = False
    for it in items:
        if it["product_id"] == req.product_id and it["size"] == req.size and it["color"] == req.color:
            it["quantity"] += req.quantity
            it["total_price"] = round(it["quantity"] * prod["price"], 2)
            matched = True
            break

    if not matched:
        item_id = f"item_{uuid.uuid4().hex[:8]}"
        items.append({
            "id": item_id,
            "product_id": req.product_id,
            "size": req.size,
            "color": req.color,
            "quantity": req.quantity,
            "unit_price": prod["price"],
            "total_price": round(prod["price"] * req.quantity, 2)
        })

    await db.cart.update_one(
        query,
        {"$set": {"items": items}},
        upsert=True
    )

    return await get_cart(current_user, x_session_id, db)

@router.put("/items/{item_id}", response_model=CartResponse)
async def update_cart_item_quantity(
    item_id: str,
    req: UpdateCartRequest,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update item quantity in shopping bag."""
    query = await get_cart_identifier(current_user, x_session_id)
    cart_doc = await db.cart.find_one(query)
    if not cart_doc or "items" not in cart_doc:
        raise HTTPException(status_code=404, detail="Shopping bag is empty.")

    items = cart_doc.get("items", [])
    if req.quantity <= 0:
        items = [it for it in items if it["id"] != item_id]
    else:
        for it in items:
            if it["id"] == item_id:
                it["quantity"] = req.quantity
                it["total_price"] = round(it["quantity"] * it.get("unit_price", 0.0), 2)
                break

    await db.cart.update_one(query, {"$set": {"items": items}})
    return await get_cart(current_user, x_session_id, db)

@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_cart_item(
    item_id: str,
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Remove item from shopping bag."""
    query = await get_cart_identifier(current_user, x_session_id)
    cart_doc = await db.cart.find_one(query)
    if cart_doc and "items" in cart_doc:
        items = [it for it in cart_doc["items"] if it["id"] != item_id]
        await db.cart.update_one(query, {"$set": {"items": items}})

    return await get_cart(current_user, x_session_id, db)

@router.delete("", response_model=CartResponse)
async def clear_cart(
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Clear all items from shopping bag."""
    query = await get_cart_identifier(current_user, x_session_id)
    await db.cart.update_one(query, {"$set": {"items": []}})
    return await get_cart(current_user, x_session_id, db)
