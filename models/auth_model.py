from pydantic import BaseModel, EmailStr
from datetime import datetime


# ---------- Request Models ----------

class RegisterRequest(BaseModel):
    """Body for POST /auth/register."""
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Body for POST /auth/login."""
    email: EmailStr
    password: str


# ---------- Document / DB Model ----------

class UserInDB(BaseModel):
    """Shape of a user document stored in MongoDB (minus _id)."""
    name: str
    email: str
    password_hash: str
    created_at: datetime


# ---------- Response Models ----------

class UserResponse(BaseModel):
    """User info returned in API responses (no password)."""
    id: str
    name: str
    email: str


class AuthResponse(BaseModel):
    """Response after login or register."""
    token: str
    user: UserResponse


class MeResponse(BaseModel):
    """Response for GET /auth/me."""
    id: str
    email: str
    name: str