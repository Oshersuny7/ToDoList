from pydantic import BaseModel,constr
from typing import Optional
from datetime import datetime

class TaskModel(BaseModel):
    text: constr(min_length=1, max_length=100) # type: ignore
    status: str = "active"
    userId: Optional[str] =None
    taskForUser :Optional[str] = None
    created_at: datetime= None

class UpdateTaskModel(BaseModel):
    text: str
    status: str
    updated_at: datetime= None

