from asyncio import gather
from fastapi import APIRouter, Body, Depends, HTTPException
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
            tasks_cursor = db.tasks.find({})
        else:
            # Regular user can see their own tasks
            tasks_cursor = db.tasks.find({"userId": payload['_id']})

        task_list = await tasks_cursor.to_list(None)

        # Check if there are tasks
        if not task_list:
            return {"tasks": []}

        # Fetch users to map user IDs to names and last names
        users_cursor = db.users.find({})
        users_dict = {str(user["_id"]): {"name": user["name"], "lastName": user["lastName"]} for user in await users_cursor.to_list(None)}

        # Add name and lastName fields to each task
        for task in task_list:
            task["_id"] = str(task["_id"])
            user_id = task.get("userId")
            if user_id in users_dict:
                task["name"] = users_dict[user_id]["name"]
                task["lastName"] = users_dict[user_id]["lastName"]
            else:
                task["name"] = ""
                task["lastName"] = ""

        return {"tasks": task_list}

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        error_detail = f"An error occurred while processing the request: {str(e)}"
        print(error_detail)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)

# Reminder
@router.get("/check-reminder/{task_id}")
async def check_reminder(task_id: str, payload: dict = Depends(getCurrentUserData)):
    try:
        # Fetch the task from the database
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})

        # Check if the authenticated user is the owner of the task
        if task["userId"] == payload["_id"]:
            # Check if the task status is not completed
            if task["status"] != "completed":
                return {"reminderApplicable": True}
            else:
                return {"reminderApplicable": False, "reason": "Task status is completed."}
        else:
            return {"reminderApplicable": False, "reason": "User ID does not match."}
    except Exception as e:
        return {"reminderApplicable": False, "reason": str(e)}

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

# Admin creates tasks for users 
@router.post("/admin/{user_id}")
async def addTaskforUser(
    user_id: str,
    task_data: dict = Body(...),
    payload: dict = Depends(getCurrentUserData)
):
    try:
        print(user_id)
        print(task_data)
        print(payload)
        # Check if the authenticated user is an admin
        if not payload.get("isAdmin", False):
            raise HTTPException(status_code=403, detail="Only admins can add tasks for users.")

        # Check if the specified user exists
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Create the task for the specified user
        new_task = {
            "userId": user_id,  
            "text": task_data['text'],      
            "status": "active",
            "created_at": task_data.get('created_at', datetime.now()),
        }

        await db.tasks.insert_one(new_task)

        return {"message": "Task added successfully."}

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        error_detail = f"An error occurred while processing the request: {str(e)}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

# Updating a task
@router.patch("/{task_id}")
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

# Deleting all completed tasks
@router.delete("/allcompletedtasks")
async def deleteAllCompletedTasks(payload: dict = Depends(getCurrentUserData)):
    try:
        print(payload["_id"])
 
        results = await gather(db.tasks.delete_many({"userId": payload["_id"], "status": "completed"}))
        response = results[0] 

        return {"message": f"All completed tasks deleted successfully. Deleted count: {response.deleted_count}"}
    
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


