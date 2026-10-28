import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.app.config import settings
from backend.app.database import db_manager
from backend.app.utils.seed_data import seed_database
from backend.app.routes import (
    health_router,
    auth_router,
    products_router,
    cart_router,
    orders_router,
    wishlist_router,
    newsletter_router
)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("outfitaura.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup initialization and shutdown cleanup."""
    logger.info("Initializing OutfitAura API services...")
    db = await db_manager.connect_async()
    
    # Auto-seed if database is empty
    if db is not None:
        try:
            prod_count = await db.products.count_documents({})
            if prod_count == 0:
                logger.info("Database is empty. Seeding initial OutfitAura luxury catalog...")
                await seed_database(db)
            else:
                logger.info("Database initialized with %d products.", prod_count)
        except Exception as e:
            logger.warning("Auto-seed check encountered an issue: %s", e)
    
    if not db_manager.is_connected:
        logger.info(
            "MongoDB Atlas is currently offline or waiting for IP whitelist. "
            "In-memory catalog fallback is active and fully functional."
        )

    yield

    logger.info("Shutting down OutfitAura API...")
    await db_manager.close()

# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Static & Frontend paths
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
js_dir = os.path.join(frontend_dir, "js")
if os.path.exists(js_dir):
    app.mount("/js", StaticFiles(directory=js_dir), name="js")

# Mount API Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(wishlist_router, prefix="/api")
app.include_router(newsletter_router, prefix="/api")

@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve OutfitAura luxury fashion homepage."""
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return RedirectResponse(url="/docs")

@app.get("/shop.html", include_in_schema=False)
@app.get("/shop", include_in_schema=False)
async def serve_shop():
    """Serve OutfitAura collection catalog."""
    shop_file = os.path.join(frontend_dir, "shop.html")
    if os.path.exists(shop_file):
        return FileResponse(shop_file)
    return RedirectResponse(url="/docs")

@app.get("/product.html", include_in_schema=False)
@app.get("/product", include_in_schema=False)
async def serve_product():
    """Serve OutfitAura product detail page."""
    prod_file = os.path.join(frontend_dir, "product.html")
    if os.path.exists(prod_file):
        return FileResponse(prod_file)
    return RedirectResponse(url="/docs")

@app.get("/api")
async def api_root():
    """API overview endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "description": "Welcome to the OutfitAura API.",
        "documentation": "/docs",
        "endpoints": {
            "health": "/api/health",
            "auth": "/api/auth",
            "products": "/api/products",
            "cart": "/api/cart",
            "orders": "/api/orders",
            "wishlist": "/api/wishlist",
            "newsletter": "/api/newsletter"
        }
    }
