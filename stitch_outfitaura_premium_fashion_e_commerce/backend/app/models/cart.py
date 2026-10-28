from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from backend.app.models.product import ProductModel

class CartItemBase(BaseModel):
    product_id: str
    size: str
    color: str
    quantity: int = Field(default=1, ge=1)

class AddToCartRequest(CartItemBase):
    pass

class UpdateCartRequest(BaseModel):
    quantity: int = Field(..., ge=0)

class CartItem(CartItemBase):
    id: str
    product: Optional[ProductModel] = None
    unit_price: float
    total_price: float

class CartResponse(BaseModel):
    user_id: Optional[str] = None
    items: List[CartItem] = []
    subtotal: float = 0.0
    shipping_fee: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    total_items: int = 0
