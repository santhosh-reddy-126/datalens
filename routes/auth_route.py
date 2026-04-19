from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone

from database.db import users_col
from models.auth_model import (
    RegisterRequest,
    LoginRequest,
    UserInDB,
    UserResponse,
    AuthResponse,
    MeResponse,
)
from utils.auth_utils import (
    hash_password,
    verify_password,
    create_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
async def register(req: RegisterRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = users_col.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = UserInDB(
        name=req.name.strip(),
        email=req.email.lower().strip(),
        password_hash=hash_password(req.password),
        created_at=datetime.now(timezone.utc),
    )

    result = users_col.insert_one(user.model_dump())
    user_id = str(result.inserted_id)

    token = create_token(user_id, user.email, user.name)

    return AuthResponse(
        token=token,
        user=UserResponse(id=user_id, name=user.name, email=user.email),
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    doc = users_col.find_one({"email": req.email.lower().strip()})

    if not doc or not verify_password(req.password, doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(doc["_id"])
    token = create_token(user_id, doc["email"], doc["name"])

    return AuthResponse(
        token=token,
        user=UserResponse(id=user_id, name=doc["name"], email=doc["email"]),
    )


@router.get("/me", response_model=MeResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return MeResponse(
        id=current_user["sub"],
        email=current_user["email"],
        name=current_user["name"],
    )