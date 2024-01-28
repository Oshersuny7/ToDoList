from fastapi import APIRouter
from .users import router as usersRouter
from .tasks import router as tasksRouter 


router = APIRouter()

router.include_router(usersRouter, prefix="/users",tags=["users"])
router.include_router(tasksRouter, prefix="/tasks",tags=["tasks"])
