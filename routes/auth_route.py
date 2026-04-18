from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone

from database.db import users_col
from models.auth_model import RegisterRequest, LoginRequest
from utils.auth_utils import (
    hash_password,
    verify_password,
    create_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = users_col.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = {
        "name": req.name.strip(),
        "email": req.email.lower().strip(),
        "password_hash": hash_password(req.password),
        "created_at": datetime.now(timezone.utc),
    }

    result = users_col.insert_one(user)
    user_id = str(result.inserted_id)

    token = create_token(user_id, req.email, req.name.strip())

    return {
        "token": token,
        "user": {"id": user_id, "name": req.name.strip(), "email": req.email},
    }


@router.post("/login")
async def login(req: LoginRequest):
    user = users_col.find_one({"email": req.email.lower().strip()})

    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    token = create_token(user_id, user["email"], user["name"])

    return {
        "token": token,
        "user": {"id": user_id, "name": user["name"], "email": user["email"]},
    }


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["sub"],
        "email": current_user["email"],
        "name": current_user["name"],
    }