import jwt
import os
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from dotenv import load_dotenv 

load_dotenv()

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def generateAuthToken(_id, name, lastName, email, isAdmin):
    if SECRET_KEY is None:
        raise ValueError("Missing JWT_SECRET_KEY in environment variables")

    expirationTime = datetime.utcnow() + timedelta(minutes=30)

    payload = {
        "_id": _id,
        "name": name,
        "lastName": lastName,
        "email": email,
        "isAdmin": isAdmin,
        "exp": expirationTime,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def getCurrentUserData(request: Request):
    token = request.cookies.get("LoggedInToken")
    if token is None:
        raise HTTPException(status_code=401, detail="Token not found in cookie")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token")
