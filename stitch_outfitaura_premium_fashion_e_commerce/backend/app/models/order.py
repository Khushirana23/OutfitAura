from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class ShippingAddress(BaseModel):
    full_name: str
    phone: str
    street: str
    apartment: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "India"

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    product_image: str
    size: str
    color: str
    price: float
    quantity: int
    subtotal: float

class OrderCreate(BaseModel):
    items: List[OrderItem]
    shipping_address: ShippingAddress
    payment_method: str = "card"  # 'card', 'upi', 'cod'
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    order_number: str
    items: List[OrderItem]
    shipping_address: ShippingAddress
    subtotal: float
    shipping_fee: float
    tax: float
    total: float
    payment_method: str
    payment_status: str = "paid"  # 'pending', 'paid', 'failed'
    order_status: str = "processing"  # 'processing', 'shipped', 'delivered', 'cancelled'
    created_at: datetime
