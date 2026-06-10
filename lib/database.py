from beanie import init_beanie 
import motor.motor_asyncio 
from config import BaseConfig
from models.cars import Car 
from models.users import User 

settings = BaseConfig() 

async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.DB_URL 
    )
    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[User, Car]
    )