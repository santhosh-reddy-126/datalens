from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ---------- Request Models ----------

class ProductRequest(BaseModel):
    """Body for POST /product — only needs a URL."""
    url: str


# ---------- Document / DB Models ----------

class ProductInDB(BaseModel):
    """Shape of a product document stored in MongoDB (minus _id)."""
    product_id: str
    url: str
    title: Optional[str] = None
    imageUrl: Optional[str] = None
    rating: Optional[float] = None
    price: Optional[float] = None
    updated_at: datetime


# ---------- Response Models ----------

class ProductResponse(BaseModel):
    """Single product returned by the API."""
    id: str
    product_id: str
    url: str
    title: Optional[str] = None
    imageUrl: Optional[str] = None
    rating: Optional[float] = None
    price: Optional[float] = None
    updated_at: Optional[datetime] = None


class ProductListResponse(BaseModel):
    """Wrapper for a list of products."""
    data: list[ProductResponse]


class ProductCreateResponse(BaseModel):
    """Response after adding a new product."""
    product_id: str
    data: dict


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str




# ---------- Document / DB Model ----------

class ProductHistoryInDB(BaseModel):
    """Shape of a product history document stored in MongoDB (minus _id)."""
    product_id: str
    price: Optional[float] = None
    created_at: datetime


# ---------- Response Models ----------

class ProductHistoryResponse(BaseModel):
    """Single history entry returned by the API."""
    id: str
    product_id: str
    price: Optional[float] = None
    created_at: datetime


class ProductHistoryListResponse(BaseModel):
    """Wrapper for a list of history entries."""
    data: list[ProductHistoryResponse]
