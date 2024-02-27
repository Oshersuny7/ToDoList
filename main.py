from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.configRoutes import router as routesRouter
from db.mongoConnect import checkMongoConnection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE","PATCH"],
    allow_headers=["Access-Control-Allow-Origin","Authorization", "Content-Type","Client-Type"],
)

app.include_router(routesRouter)

# Check MongoDB connection at startup
@app.on_event("startup")
async def startup_event():
    await checkMongoConnection()

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 5000))
    
    uvicorn.run(app, host="0.0.0.0", port=port)
