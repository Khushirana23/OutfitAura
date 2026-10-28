import uuid
import re
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.app.database import get_database
from backend.app.models.product import (
    ProductModel, 
    ProductCreate, 
    ProductUpdate, 
    ProductListResponse
)
from backend.app.models.review import ReviewCreate, ReviewResponse
from backend.app.models.user import UserResponse
from backend.app.utils.auth import get_current_user, get_current_user_optional

router = APIRouter(prefix="/products", tags=["Product Catalog"])

@router.get("", response_model=ProductListResponse)
async def list_products(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    size: Optional[str] = None,
    is_new_arrival: Optional[bool] = None,
    is_trending: Optional[bool] = None,
    is_sale: Optional[bool] = None,
    sort_by: Optional[str] = Query("newest", pattern="^(price_asc|price_desc|newest|rating|popular)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Retrieve and filter products with pagination and multiple sorting options."""
    query = {}
    
    if category:
        # Match case-insensitively or exact
        query["category"] = {"$regex": f"^{re.escape(category)}$", "$options": "i"}
    if subcategory:
        query["subcategory"] = {"$regex": f"^{re.escape(subcategory)}$", "$options": "i"}
    if search:
        search_regex = {"$regex": re.escape(search), "$options": "i"}
        query["$or"] = [
            {"name": search_regex},
            {"description": search_regex},
            {"tags": search_regex},
            {"category": search_regex}
        ]
    
    # Price filtering
    price_cond = {}
    if min_price is not None:
        price_cond["$gte"] = min_price
    if max_price is not None:
        price_cond["$lte"] = max_price
    if price_cond:
        query["price"] = price_cond
        
    if size:
        query["sizes"] = size
    if is_new_arrival is not None:
        query["is_new_arrival"] = is_new_arrival
    if is_trending is not None:
        query["is_trending"] = is_trending
    if is_sale is not None:
        query["is_sale"] = is_sale

    # Sorting
    sort_map = {
        "price_asc": ("price", 1),
        "price_desc": ("price", -1),
        "newest": ("created_at", -1),
        "rating": ("rating", -1),
        "popular": ("review_count", -1)
    }
    sort_field, sort_order = sort_map.get(sort_by, ("created_at", -1))

    total = await db.products.count_documents(query)
    skip = (page - 1) * limit
    
    cursor = db.products.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    
    products = []
    for doc in docs:
        doc["id"] = str(doc.get("id") or doc.get("_id"))
        products.append(ProductModel(**doc))

    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return ProductListResponse(
        products=products,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )

@router.get("/featured", response_model=List[ProductModel])
async def get_featured_products(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Retrieve featured products for lookbooks and hero spotlights."""
    cursor = db.products.find({"is_featured": True}).limit(8)
    docs = await cursor.to_list(length=8)
    return [ProductModel(**{**doc, "id": str(doc.get("id") or doc.get("_id"))}) for doc in docs]

@router.get("/categories")
async def get_categories(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Retrieve distinct categories and subcategories."""
    categories = await db.products.distinct("category")
    subcategories = await db.products.distinct("subcategory")
    return {
        "categories": categories,
        "subcategories": [s for s in subcategories if s]
    }

@router.get("/{id_or_slug}", response_model=ProductModel)
async def get_product(id_or_slug: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Retrieve product details by product ID or URL slug."""
    doc = await db.products.find_one({"$or": [{"id": id_or_slug}, {"slug": id_or_slug}]})
    if not doc:
        # Check by _id
        from bson import ObjectId
        try:
            doc = await db.products.find_one({"_id": ObjectId(id_or_slug)})
        except Exception:
            pass

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{id_or_slug}' not found."
        )

    doc["id"] = str(doc.get("id") or doc.get("_id"))
    return ProductModel(**doc)

@router.post("", response_model=ProductModel, status_code=status.HTTP_201_CREATED)
async def create_product(
    prod_in: ProductCreate, 
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new product catalog entry."""
    prod_id = f"prod_{uuid.uuid4().hex[:10]}"
    prod_doc = prod_in.dict()
    prod_doc["id"] = prod_id
    prod_doc["created_at"] = datetime.utcnow()
    
    await db.products.insert_one(prod_doc)
    return ProductModel(**prod_doc)

@router.get("/{product_id}/reviews", response_model=List[ReviewResponse])
async def get_product_reviews(product_id: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Retrieve customer reviews for a given product."""
    cursor = db.reviews.find({"product_id": product_id}).sort("created_at", -1)
    docs = await cursor.to_list(length=100)
    return [ReviewResponse(**{**doc, "id": str(doc.get("id") or doc.get("_id"))}) for doc in docs]

@router.post("/{product_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_product_review(
    product_id: str,
    rev_in: ReviewCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Add a customer review and rating for a product."""
    prod = await db.products.find_one({"id": product_id})
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found.")

    rev_id = f"rev_{uuid.uuid4().hex[:10]}"
    rev_doc = {
        "id": rev_id,
        "product_id": product_id,
        "user_id": current_user.id,
        "user_name": current_user.full_name,
        "rating": rev_in.rating,
        "title": rev_in.title,
        "comment": rev_in.comment,
        "size_purchased": rev_in.size_purchased,
        "color_purchased": rev_in.color_purchased,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.reviews.insert_one(rev_doc)

    # Recalculate average rating for product
    all_revs = await db.reviews.find({"product_id": product_id}).to_list(length=1000)
    if all_revs:
        avg_rating = sum(r["rating"] for r in all_revs) / len(all_revs)
        await db.products.update_one(
            {"id": product_id},
            {"$set": {"rating": round(avg_rating, 1), "review_count": len(all_revs)}}
        )

    return ReviewResponse(**rev_doc)
