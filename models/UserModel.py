from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

class UserModel(BaseModel):
    name: constr(min_length=3, max_length=12) # type: ignore
    lastName: constr(min_length=3, max_length=12) # type: ignore
    email: EmailStr  
    password: str
    isAdmin: bool = False
    created_at: datetime = None
