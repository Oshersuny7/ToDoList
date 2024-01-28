from fastapi import APIRouter, HTTPException,Response,Depends
from models.UserModel import UserModel
from utils.hashPassword import hashPassword
from utils.hashPassword import comparePasswords
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

# Get the token
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
           
# SignUp
@router.post("/signup")
async def signUp(userData: UserModel,Response: Response):
    try:
        userData.created_at = datetime.now()
        existingUser = await db.users.find_one({"email":userData.email})
        if existingUser:
            raise HTTPException(status_code=400,detail="User with this email alredy exist")
        # Hash the password
        hashedPassword = hashPassword(userData.password)
        userData.password = hashedPassword
        # Create the user
        db.users.insert_one(userData.model_dump())
        # Generate auth token and set it as a cookie
        accessToken = generateAuthToken(
            str(userData), userData.name, userData.lastName, userData.email, userData.isAdmin
        )
        Response.set_cookie(key="token:",value=accessToken,max_age=3600,httponly=True)
        return {"accessToken":accessToken}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# SignIn
@router.post("/signin")
async def signIn(signInData: SignInData, response: Response):
    try:
        user = await db.users.find_one({"email": signInData.email})
        if user:
            if comparePasswords(signInData.password, user["password"]):
                accessToken = generateAuthToken(
                    str(user["_id"]), user["name"], user["lastName"], user["email"], user["isAdmin"]
                )
                response.set_cookie(key="LoggedInToken", value = accessToken, max_age=3600, httponly=True)
                return {"accessToken": accessToken}
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except Exception as e:
        logging.error("Error during sign-in: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error:{str(e)}")


