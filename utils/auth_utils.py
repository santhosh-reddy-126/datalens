import os
import hashlib
import hmac
import base64
import json
import time
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

SECRET_KEY = os.getenv("JWT_SECRET", "datalens-super-secret-key-2024")
TOKEN_EXPIRE_SECONDS = 7 * 24 * 3600

security = HTTPBearer()


# ---------- password ----------

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260000)
    return base64.b64encode(salt + dk).decode()


def verify_password(password: str, stored: str) -> bool:
    raw = base64.b64decode(stored.encode())
    salt, dk = raw[:16], raw[16:]
    new_dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260000)
    return hmac.compare_digest(dk, new_dk)


# ---------- jwt ----------

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

        expected_sig = _b64url_encode(
            hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).digest()
        )

        if not hmac.compare_digest(sig, expected_sig):
            raise ValueError("Invalid signature")

        data = json.loads(_b64url_decode(payload))

        if data.get("exp", 0) < int(time.time()):
            raise ValueError("Token expired")

        return data

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    return decode_token(credentials.credentials)