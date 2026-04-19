from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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
