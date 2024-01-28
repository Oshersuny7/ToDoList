from pydantic import BaseModel
from datetime import datetime

class UserModel(BaseModel):
    name: str
    lastName: str
    email: str
    password: str
    isAdmin: bool = False
    created_at: datetime= None

