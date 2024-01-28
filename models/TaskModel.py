from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskModel(BaseModel):
    text: str
    status: str
    userId: Optional[str] =None
    taskForUser :Optional[str] = None
    created_at: datetime= None


class UpdateTaskModel(BaseModel):
    text: str
    status: str
    updated_at: datetime= None

