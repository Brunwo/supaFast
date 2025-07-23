from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TokenData(BaseModel):
    user_id: str
    role: str
    email: Optional[str] = None
    exp: datetime
    aud: Optional[str] = None
    iss: Optional[str] = None
    is_anonymous : bool = True