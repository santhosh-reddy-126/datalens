from pydantic import BaseModel
from datetime import datetime



# ---------- Document / DB Models ----------

class UsersTrackInDB(BaseModel):
    """ Users Product Linkage Document """
    product_id: str
    email: str
    created_at: datetime 
