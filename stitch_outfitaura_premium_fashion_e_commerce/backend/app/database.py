import certifi
import logging
import re
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database

from backend.app.config import settings

logger = logging.getLogger("outfitaura.database")


class MockCursor:
    """Mock asynchronous cursor for in-memory collections."""
    def __init__(self, data: List[Dict[str, Any]]):
        self._data = list(data)

    def sort(self, key_or_list, direction=1):
        if isinstance(key_or_list, list):
            for k, d in reversed(key_or_list):
                self._data.sort(key=lambda x: x.get(k, 0) or 0, reverse=(d == -1))
        elif isinstance(key_or_list, str):
            self._data.sort(key=lambda x: x.get(key_or_list, 0) or 0, reverse=(direction == -1))
        return self

    def skip(self, n: int):
        self._data = self._data[n:]
        return self

    def limit(self, n: int):
        self._data = self._data[:n]
        return self

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        if length is not None:
            return [dict(d) for d in self._data[:length]]
        return [dict(d) for d in self._data]


class MockCollection:
    """In-memory MongoDB-compatible async collection fallback."""
    def __init__(self, name: str):
        self.name = name
        self._docs: List[Dict[str, Any]] = []

    def _matches_filter(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        for k, v in query.items():
            if k == "$or":
                if not any(self._matches_filter(doc, sub) for sub in v):
                    return False
            elif k == "$and":
                if not all(self._matches_filter(doc, sub) for sub in v):
                    return False
            elif isinstance(v, dict):
                val = doc.get(k)
                if "$regex" in v:
                    opts = v.get("$options", "")
                    flags = re.IGNORECASE if "i" in opts else 0
                    if not (isinstance(val, str) and re.search(v["$regex"], val, flags)):
                        return False
                if "$gte" in v and not (val is not None and val >= v["$gte"]):
                    return False
                if "$lte" in v and not (val is not None and val <= v["$lte"]):
                    return False
                if "$in" in v and val not in v["$in"]:
                    return False
            else:
                doc_val = doc.get(k)
                if isinstance(doc_val, list):
                    if v not in doc_val:
                        return False
                elif doc_val != v:
                    return False
        return True

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for d in self._docs:
            if self._matches_filter(d, query):
                return dict(d)
        return None

    def find(self, query: Optional[Dict[str, Any]] = None) -> MockCursor:
        query = query or {}
        matched = [dict(d) for d in self._docs if self._matches_filter(d, query)]
        return MockCursor(matched)

    async def count_documents(self, query: Dict[str, Any]) -> int:
        return sum(1 for d in self._docs if self._matches_filter(d, query))

    async def insert_one(self, doc: Dict[str, Any]):
        self._docs.append(dict(doc))
        return type("InsertResult", (), {"inserted_id": doc.get("id")})()

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        target = None
        for d in self._docs:
            if self._matches_filter(d, query):
                target = d
                break

        if target:
            if "$set" in update:
                target.update(update["$set"])
            if "$inc" in update:
                for k, v in update["$inc"].items():
                    target[k] = target.get(k, 0) + v
            return type("UpdateResult", (), {"matched_count": 1, "modified_count": 1})()
        elif upsert:
            new_doc = dict(query)
            if "$set" in update:
                new_doc.update(update["$set"])
            self._docs.append(new_doc)
            return type("UpdateResult", (), {"matched_count": 0, "modified_count": 0, "upserted_id": new_doc.get("id")})()
        
        return type("UpdateResult", (), {"matched_count": 0, "modified_count": 0})()

    async def delete_one(self, query: Dict[str, Any]):
        for i, d in enumerate(self._docs):
            if self._matches_filter(d, query):
                del self._docs[i]
                return type("DeleteResult", (), {"deleted_count": 1})()
        return type("DeleteResult", (), {"deleted_count": 0})()

    async def distinct(self, key: str) -> List[Any]:
        results = set()
        for d in self._docs:
            val = d.get(key)
            if val is not None:
                if isinstance(val, list):
                    results.update(val)
                else:
                    results.add(val)
        return list(results)

    async def create_index(self, keys, **kwargs):
        pass


class MockDatabase:
    """Mock asynchronous database containing collections."""
    def __init__(self):
        self._collections: Dict[str, MockCollection] = {}
        self._preseed()

    def _preseed(self):
        from backend.app.utils.initial_data import SEED_PRODUCTS, SEED_REVIEWS
        for p in SEED_PRODUCTS:
            self.products._docs.append(dict(p))
        for r in SEED_REVIEWS:
            self.reviews._docs.append(dict(r))

    def __getattr__(self, item: str) -> MockCollection:
        if item not in self._collections:
            self._collections[item] = MockCollection(item)
        return self._collections[item]

    def __getitem__(self, item: str) -> MockCollection:
        return self.__getattr__(item)


class DatabaseManager:
    """Manages MongoDB connections with graceful async client pooling and diagnostics."""
    
    def __init__(self):
        self.async_client: Optional[AsyncIOMotorClient] = None
        self.async_db: Optional[AsyncIOMotorDatabase] = None
        self.mock_db: MockDatabase = MockDatabase()
        self.sync_client: Optional[MongoClient] = None
        self.sync_db: Optional[Database] = None
        self.is_connected: bool = False
        self.using_fallback: bool = False
        self.last_error: Optional[str] = None

    def get_client_options(self) -> Dict[str, Any]:
        """Provides MongoDB client TLS options with certifi certificates."""
        return {
            "serverSelectionTimeoutMS": 3000,
            "connectTimeoutMS": 5000,
            "socketTimeoutMS": 10000,
            "retryWrites": True,
            "tlsCAFile": certifi.where()
        }

    async def connect_async(self) -> Any:
        """Initializes the async Motor client connection or activates local fallback."""
        if self.async_db is not None and self.is_connected:
            return self.async_db

        try:
            opts = self.get_client_options()
            logger.info("Connecting to MongoDB Atlas at %s...", settings.MONGODB_URI.split("@")[-1] if "@" in settings.MONGODB_URI else "URI")
            self.async_client = AsyncIOMotorClient(settings.MONGODB_URI, **opts)
            self.async_db = self.async_client[settings.DB_NAME]
            
            # Verify connectivity
            await self.async_client.admin.command('ping')
            self.is_connected = True
            self.using_fallback = False
            self.last_error = None
            logger.info("Successfully connected to MongoDB Atlas database '%s'", settings.DB_NAME)
            return self.async_db
        except Exception as exc:
            self.is_connected = False
            self.using_fallback = True
            self.last_error = str(exc)
            logger.warning(
                "MongoDB Atlas connection attempt failed (%s). "
                "Activating in-memory fallback store for offline development while IP whitelist is pending.",
                exc
            )
            return self.mock_db

    async def check_health(self) -> Dict[str, Any]:
        """Runs a ping command to test MongoDB status."""
        try:
            if not self.async_client:
                await self.connect_async()
            
            if self.async_client:
                res = await self.async_client.admin.command('ping')
                self.is_connected = True
                self.using_fallback = False
                return {
                    "status": "connected",
                    "mode": "mongodb_atlas",
                    "database": settings.DB_NAME,
                    "ping": res.get("ok", 1.0),
                    "cluster": settings.MONGODB_URI.split("@")[-1].split("/")[0] if "@" in settings.MONGODB_URI else "cluster0"
                }
        except Exception as e:
            return {
                "status": "fallback_active",
                "mode": "in_memory_catalog",
                "database": settings.DB_NAME,
                "error": str(e),
                "hint": "Ensure your IP address is whitelisted in MongoDB Atlas under Network Access (0.0.0.0/0 or current IP)."
            }
        
        return {
            "status": "fallback_active",
            "mode": "in_memory_catalog",
            "database": settings.DB_NAME,
            "error": self.last_error
        }

    async def close(self):
        """Closes all active database connections."""
        if self.async_client:
            self.async_client.close()
            logger.info("Closed MongoDB async client.")
        if self.sync_client:
            self.sync_client.close()
            logger.info("Closed MongoDB sync client.")


db_manager = DatabaseManager()

async def get_database() -> Any:
    """FastAPI dependency for accessing the database."""
    if db_manager.is_connected and db_manager.async_db is not None:
        return db_manager.async_db
    if db_manager.using_fallback:
        return db_manager.mock_db
    return await db_manager.connect_async()
