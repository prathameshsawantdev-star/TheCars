from unittest import result

from fastapi import FastAPI 
from contextlib import asynccontextmanager 
from authentication import AuthHandler
from config import BaseConfig
from motor import motor_asyncio 

from routers.cars import router as cars_router 
from routers.users import router as users_router 
from fastapi.middleware.cors import CORSMiddleware 
settings = BaseConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # add logic to add required collections if they do not exist in DB 
    print("Starting up...")
    app.client = motor_asyncio.AsyncIOMotorClient(settings.DB_URL)
    app.db = app.client[settings.DB_NAME]
    try:
        await app.client.admin.command("ping")
        result = await app.db.test.insert_one({
        "message": "startup test"
        })
        print(result.inserted_id)
        print("Pinged your deployment. You successfully connected to MongoDB!")
        print("MongoDB address:", settings.DB_URL)
    except Exception as e:
        print(f"Error connecting to the database: {e}")
    yield
    app.client.close()
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(cars_router, prefix="/cars", tags=["cars"])
app.include_router(users_router, prefix="/users", tags=["users"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root_route():
    return {"message": "Hello World!"}