from fastapi import HTTPException
import bcrypt
from dotenv import load_dotenv
import os
import base64
load_dotenv()

PEPPER = os.environ.get("PEPPER")

def hashPassword(password: str) -> str:
    decodedData = base64.b64decode(password).decode("utf-8")
    if len(decodedData) >= 3 and len(decodedData) <= 16:
        pepperedPassword = decodedData + PEPPER
        print(pepperedPassword)
        salt = bcrypt.gensalt(10)
        hashedPassword = bcrypt.hashpw(pepperedPassword.encode('utf-8'), salt)
        print(pepperedPassword)
        return hashedPassword.decode('utf-8')
    else:
        raise HTTPException(status_code=401, detail="Password must be between 3 and 16 characters")
    
def comparePasswords(plainPassword, hashedPassword):
    try:
        pepperedPassword = plainPassword + PEPPER
        print(hashedPassword, pepperedPassword)

        return bcrypt.checkpw(pepperedPassword.encode('utf-8'), hashedPassword.encode('utf-8'))
    except Exception as e:
        print("Error:", str(e))
        return False

 