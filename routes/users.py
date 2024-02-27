import base64
from fastapi import APIRouter, HTTPException,Response,Depends
from models.UserModel import UserModel
from utils.hashPassword import hashPassword,comparePasswords
from utils.generateAuthToken import generateAuthToken
from utils.generateAuthToken import getCurrentUserData
from fastapi import APIRouter, HTTPException
from db.mongoConnect import db
from pydantic import BaseModel
import logging
from datetime import datetime

router = APIRouter()

class SignInData(BaseModel):
    email: str
    password: str

# Get the role
@router.get("/getrole")
async def getRole(payload: dict = Depends(getCurrentUserData)):
    try:
        # Retrieve the isAdmin value from the payload
        isAdmin = payload.get('isAdmin', False)

        return {"isAdmin": isAdmin}

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        error_detail = f"An error occurred while processing the request: {str(e)}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

# Admin see all users
@router.get("/admin")
async def getUsers(payload: dict = Depends(getCurrentUserData)):
    try:
        if payload["isAdmin"]:
            # Fetch all users
            users_cursor = db.users.find()
            
            # Convert the cursor to a list
            users_list = await users_cursor.to_list(length=100)

            # Modify the data if needed
            for user in users_list:
                user["_id"] = str(user["_id"])
                
            # Check if there are users
            if not users_list:
                return {"users": []}

            return {"all_users": users_list}

        else:
            raise HTTPException(status_code=403, detail="Forbidden. User is not an admin.")

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        error_detail = f"An error occurred while processing the request: {str(e)}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

# SignUp
@router.post("/signup")
async def signUp(userData: UserModel, Response: Response):
    try:
        userData.created_at = datetime.now()
        existingUser = await db.users.find_one({"email": userData.email})
        if existingUser:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Hash the password
        hashedPassword = hashPassword(userData.password)
        userData.password = hashedPassword

        # Create the user and retrieve the inserted document
        inserted_user = await db.users.insert_one(userData.model_dump())
    
        # Generate auth token and set it as a cookie
        accessToken = generateAuthToken(
            str(inserted_user.inserted_id),
            userData.name,
            userData.lastName,
            userData.email,
            userData.isAdmin
        )
        Response.set_cookie(
            key="accessToken",
            value=accessToken,
            max_age=3600,
            httponly=True,
            secure=True,
            samesite=None
        )

        return {"accessToken": accessToken}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# SignIn
@router.post("/signin")
async def signIn(signInData: SignInData, response: Response):
    try:
        decodedData = base64.b64decode(signInData.password).decode("utf-8")
        print(decodedData)
        signInData.password = decodedData
        user = await db.users.find_one({"email": signInData.email})
        if user:
            if comparePasswords(plainPassword=signInData.password, hashedPassword=user["password"]):
                accessToken = generateAuthToken(    
                    str(user["_id"]), user["name"], user["lastName"], user["email"], user["isAdmin"]
                )
                response.set_cookie(key="accessToken", value = accessToken, max_age=3600, httponly=True,secure=True,samesite=None)
                return {"accessToken": accessToken, "isAdmin":user["isAdmin"]}
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error("Error during sign-in: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error:{str(e)}")

# LogOut
@router.get("/logout")
async def logOut(response: Response):
    try:
        response = Response(content="Logout successful", media_type="text/plain")
        response.delete_cookie(key="accessToken")
        return response

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        error_detail = f"An error occurred during logout: {str(e)}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)
