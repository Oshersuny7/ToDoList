from fastapi import APIRouter, Depends, HTTPException
from models.TaskModel import TaskModel
from models.TaskModel import UpdateTaskModel
from utils.generateAuthToken import getCurrentUserData
from datetime import datetime
from db.mongoConnect import db
from bson import ObjectId 
import traceback

router = APIRouter()

# Get tasks
@router.get("/")
async def getTasks(payload: dict = Depends(getCurrentUserData)):
    try:
        # Check if the user is an admin
        if payload["isAdmin"]:
            # Admin can see all tasks
            tasks_cursor = db.tasks.find({},{"_id":0})
        else:
            # Regular user can see their own tasks
            tasks_cursor = db.tasks.find({"userId": payload['_id']},{"_id":0})
        task_list = await tasks_cursor.to_list(None)

        # Check if there are tasks
        if not task_list:
            return {"tasks": []}

        return {"tasks": task_list}

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        error_detail = f"An error occurred while processing the request: {str(e)}"
        print(error_detail)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)

# Creating new tasks
@router.post("/")
async def createTask(task: TaskModel, payload: dict = Depends(getCurrentUserData)):
    try:
        task.created_at = datetime.now()
        if payload['isAdmin'] == 'admin':
            if db.users.find_one({"_id": ObjectId(task.taskForUser)}):
                task.userId = task.taskForUser
            else:
                raise HTTPException(status_code=400, detail="Invalid userId")
        else:
            print(payload)
            task.userId = payload['_id']
            
        taskDict = task.model_dump()
        taskDict.pop('taskForUser', None)
        db.tasks.insert_one(taskDict)
        return {"task": task}
    except Exception as e:
        print(e)
        traceback.print_exc()  
        raise HTTPException(status_code=400, detail="An error occurred while processing the request")     

# Updating a task
@router.put("/{task_id}")
async def updateTask(task_id: str, updated_task:UpdateTaskModel , payload: dict = Depends(getCurrentUserData)):
    try:
        updated_task.updated_at = datetime.now()
        # Check if the task exists
        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Check if the user has permission to update the task 
        updated_task.updated_at = datetime.now()
        if payload['isAdmin'] == True:
            # Update the task
            db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": updated_task.model_dump()})
            return {"message": "Task updated successfully"}
        
        # Check if the user has permission to update the task and if so update
        else:
            db.tasks.update_one({"_id": ObjectId(task_id),"userId":payload["_id"]}, {"$set": updated_task.model_dump()})
            return {"message": "Task updated successfully"}
       
        
    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        error_detail = f"An error occurred while processing the request: {str(e)}"
        print(error_detail)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)

# Deleting a task
@router.delete("/{task_id}")
async def deleteTask(task_id: str, payload: dict = Depends(getCurrentUserData)):
    try:
        # Check if the task exists
        task = db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Check if the user has permission to delete the task and if so delete
        if payload['isAdmin']:
            db.tasks.delete_one({"_id": ObjectId(task_id)})
            return {"message": "Task deleted successfully"}
        else:
    
             db.tasks.delete_one({"_id": ObjectId(task_id),"userId":payload["_id"]})
        return {"message": "Task deleted successfully"}
    
    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        error_detail = f"An error occurred while processing the request: {str(e)}"
        print(error_detail)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)

