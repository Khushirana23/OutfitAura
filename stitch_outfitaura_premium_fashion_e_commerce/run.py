#!/usr/bin/env python3
import sys
import argparse
import asyncio
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from backend.app.config import settings
from backend.app.database import db_manager
from backend.app.utils.seed_data import seed_database

async def seed():
    print(f"Connecting to MongoDB Atlas database '{settings.DB_NAME}'...")
    db = await db_manager.connect_async()
    if not db_manager.is_connected:
        print(f"\n[Warning] Could not connect to MongoDB Atlas.")
        print(f"Details: {db_manager.last_error}")
        print("\nNote: Please make sure your current IP address is whitelisted in MongoDB Atlas under 'Network Access'.")
        return False
    
    print("Seeding database with OutfitAura catalog, users, and reviews...")
    res = await seed_database(db)
    print(f"Seeding completed successfully: {res}")
    await db_manager.close()
    return True

def main():
    parser = argparse.ArgumentParser(description="OutfitAura Backend Server Runner")
    parser.add_argument("--seed", action="store_true", help="Seed the MongoDB database with initial catalog data and exit")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Port to run the server on (default: 8000)")
    parser.add_argument("--host", type=str, default=settings.HOST, help="Host to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload in development")
    
    args = parser.parse_args()

    if args.seed:
        success = asyncio.run(seed())
        sys.exit(0 if success else 1)

    print("\n" + "=" * 60)
    print("  ✦ OutfitAura Premium Fashion E-Commerce Backend ✦")
    print("=" * 60)
    print(f"  API Docs (Swagger): http://localhost:{args.port}/docs")
    print(f"  ReDoc Docs:         http://localhost:{args.port}/redoc")
    print(f"  Health Endpoint:    http://localhost:{args.port}/api/health")
    print(f"  MongoDB Database:   {settings.DB_NAME}")
    print("=" * 60 + "\n")

    uvicorn.run(
        "backend.app.main:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )

if __name__ == "__main__":
    main()
