import uuid
from datetime import datetime
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from backend.app.utils.auth import hash_password
from backend.app.utils.initial_data import SEED_PRODUCTS, SEED_REVIEWS

logger = logging.getLogger("outfitaura.seeder")

SEED_USERS: List[Dict[str, Any]] = [
    {
        "id": "user_demo_01",
        "email": "demo@outfitaura.com",
        "password_hash": hash_password("password123"),
        "full_name": "Aura Muse",
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
        "role": "customer",
        "wishlist": ["prod_silk_slip_01", "prod_linen_blazer_02"],
        "created_at": datetime.utcnow()
    },
    {
        "id": "user_admin_01",
        "email": "admin@outfitaura.com",
        "password_hash": hash_password("admin123"),
        "full_name": "OutfitAura Director",
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80",
        "role": "admin",
        "wishlist": [],
        "created_at": datetime.utcnow()
    }
]

async def seed_database(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """Populates MongoDB collections with initial data and builds unique indexes."""
    results = {}
    try:
        # 1. Seed Products
        await db.products.create_index("slug", unique=True)
        await db.products.create_index("category")
        await db.products.create_index("tags")
        
        for prod in SEED_PRODUCTS:
            prod_copy = prod.copy()
            prod_copy["created_at"] = datetime.utcnow()
            await db.products.update_one(
                {"id": prod["id"]},
                {"$set": prod_copy},
                upsert=True
            )
        prod_count = await db.products.count_documents({})
        results["products"] = prod_count
        logger.info("Seeded %d products.", prod_count)

        # 2. Seed Users
        await db.users.create_index("email", unique=True)
        for user in SEED_USERS:
            await db.users.update_one(
                {"email": user["email"]},
                {"$set": user},
                upsert=True
            )
        user_count = await db.users.count_documents({})
        results["users"] = user_count
        logger.info("Seeded %d users.", user_count)

        # 3. Seed Reviews
        await db.reviews.create_index("product_id")
        for rev in SEED_REVIEWS:
            await db.reviews.update_one(
                {"id": rev["id"]},
                {"$set": rev},
                upsert=True
            )
        rev_count = await db.reviews.count_documents({})
        results["reviews"] = rev_count
        logger.info("Seeded %d reviews.", rev_count)

        # 4. Create Indexes for Orders & Newsletter
        await db.orders.create_index("user_id")
        await db.orders.create_index("order_number", unique=True)
        await db.newsletter.create_index("email", unique=True)
        await db.cart.create_index("user_id")

        results["status"] = "success"
    except Exception as e:
        logger.error("Error seeding database: %s", e)
        results["status"] = "error"
        results["error"] = str(e)

    return results
