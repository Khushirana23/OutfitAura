from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ProductColor(BaseModel):
    name: str
    hex: str
    image: Optional[str] = None

class ProductBase(BaseModel):
    name: str
    slug: str
    category: str
    subcategory: Optional[str] = None
    price: float = Field(..., gt=0)
    original_price: Optional[float] = None
    description: str
    details: List[str] = []
    images: List[str] = []
    thumbnail: str
    colors: List[ProductColor] = []
    sizes: List[str] = ["XS", "S", "M", "L", "XL"]
    stock: int = Field(default=50, ge=0)
    rating: float = Field(default=5.0, ge=0, le=5.0)
    review_count: int = Field(default=0, ge=0)
    is_featured: bool = False
    is_new_arrival: bool = False
    is_trending: bool = False
    is_sale: bool = False
    tags: List[str] = []

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    description: Optional[str] = None
    details: Optional[List[str]] = None
    images: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    colors: Optional[List[ProductColor]] = None
    sizes: Optional[List[str]] = None
    stock: Optional[int] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    is_featured: Optional[bool] = None
    is_new_arrival: Optional[bool] = None
    is_trending: Optional[bool] = None
    is_sale: Optional[bool] = None
    tags: Optional[List[str]] = None

class ProductModel(ProductBase):
    id: str
    created_at: Optional[datetime] = None

class ProductFilter(BaseModel):
    category: Optional[str] = None
    subcategory: Optional[str] = None
    search: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    size: Optional[str] = None
    color: Optional[str] = None
    is_new_arrival: Optional[bool] = None
    is_trending: Optional[bool] = None
    is_sale: Optional[bool] = None
    sort_by: Optional[str] = "newest"  # 'price_asc', 'price_desc', 'newest', 'rating', 'popular'
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=12, ge=1, le=100)

class ProductListResponse(BaseModel):
    products: List[ProductModel]
    total: int
    page: int
    limit: int
    total_pages: int
