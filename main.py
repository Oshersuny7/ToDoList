from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routes.configRoutes import router as routesRouter
from db.mongoConnect import checkMongoConnection

app = FastAPI()

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
