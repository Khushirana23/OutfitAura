import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.app.database import get_database
from backend.app.models.user import UserCreate, UserLogin, UserResponse, Token
from backend.app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Register a new customer account."""
    existing = await db.users.find_one({"email": user_in.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user_id = f"user_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    user_doc = {
        "id": user_id,
        "email": user_in.email.lower(),
        "password_hash": hash_password(user_in.password),
        "full_name": user_in.full_name,
        "avatar_url": user_in.avatar_url or "",
        "role": user_in.role or "customer",
        "wishlist": [],
        "created_at": now
    }
    
    await db.users.insert_one(user_doc)

    user_res = UserResponse(
        id=user_id,
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        avatar_url=user_doc["avatar_url"],
        role=user_doc["role"],
        created_at=user_doc["created_at"],
        wishlist=user_doc["wishlist"]
    )
    
    token = create_access_token({
        "sub": user_id,
        "email": user_res.email,
        "role": user_res.role
    })

    return Token(access_token=token, token_type="bearer", user=user_res)

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Authenticate existing user and return a JWT access token."""
    user_doc = await db.users.find_one({"email": user_in.email.lower()})
    if not user_doc or not verify_password(user_in.password, user_doc.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    user_res = UserResponse(
        id=str(user_doc.get("id") or user_doc.get("_id")),
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        avatar_url=user_doc.get("avatar_url"),
        role=user_doc.get("role", "customer"),
        created_at=user_doc.get("created_at", datetime.now(timezone.utc)),
        wishlist=user_doc.get("wishlist", [])
    )

    token = create_access_token({
        "sub": user_res.id,
        "email": user_res.email,
        "role": user_res.role
    })

    return Token(access_token=token, token_type="bearer", user=user_res)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Retrieve details for the currently authenticated user."""
    return current_user
