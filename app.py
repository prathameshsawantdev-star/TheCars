from unittest import result

from fastapi import FastAPI 
from contextlib import asynccontextmanager 
from authentication import AuthHandler
from config import BaseConfig
from motor import motor_asyncio 

from routers.cars import router as cars_router 
from routers.users import router as users_router 
from fastapi.middleware.cors import CORSMiddleware 
from lib.database import init_db
from fastapi_cors import CORS

settings = BaseConfig()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # add logic to add required collections if they do not exist in DB 
    print("Starting up...")
    await init_db()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
     allow_origins=["*"],           # List of allowed domains
    allow_credentials=True,         # Allow cookies and auth headers
    allow_methods=["*"],            # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"], 
)
app.include_router(cars_router, prefix="/cars", tags=["Cars"])
app.include_router(users_router, prefix="/users", tags=["Users"])


@app.get("/", tags=["Root"])
async def root_route() -> dict:
    return {"message": "Hello World!"}