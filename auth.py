import os
import hashlib
import hmac
import base64
import json
import time
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from db import db

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

users_col = db["users"]
users_col.create_index("email", unique=True)

SECRET_KEY = os.getenv("JWT_SECRET", "datalens-super-secret-key-2024")
TOKEN_EXPIRE_SECONDS = 7 * 24 * 3600  # 7 days


# ---------- helpers ----------

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260000)
    return base64.b64encode(salt + dk).decode()


def verify_password(password: str, stored: str) -> bool:
    raw = base64.b64decode(stored.encode())
    salt, dk = raw[:16], raw[16:]
    new_dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260000)
    return hmac.compare_digest(dk, new_dk)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    pad = 4 - len(s) % 4
    if pad != 4:
        s += "=" * pad
    return base64.urlsafe_b64decode(s)


def create_token(user_id: str, email: str, name: str) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(json.dumps({
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS,
    }).encode())
    msg = f"{header}.{payload}".encode()
    sig = _b64url_encode(hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).digest())
    return f"{header}.{payload}.{sig}"


def decode_token(token: str) -> dict:
    try:
        header, payload, sig = token.split(".")
        msg = f"{header}.{payload}".encode()
        expected_sig = _b64url_encode(hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected_sig):
            raise ValueError("Invalid signature")
        data = json.loads(_b64url_decode(payload))
        if data.get("exp", 0) < int(time.time()):
            raise ValueError("Token expired")
        return data
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return decode_token(credentials.credentials)


# ---------- schemas ----------

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- routes ----------

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


@router.post("/login", status_code=status.HTTP_200_OK)
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


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["sub"],
        "email": current_user["email"],
        "name": current_user["name"],
    }
