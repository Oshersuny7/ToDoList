import os
import motor.motor_asyncio
from dotenv import load_dotenv 
load_dotenv()

MONGO_DB_URI = os.environ.get("MONGO_DB")

if not MONGO_DB_URI:
    raise ValueError("Missing required environment variable: MONGO_DB")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_URI)
db=client["todolist"]

# Check MongoDB connection at startup
async def checkMongoConnection():
    try:
        await client.server_info()
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
