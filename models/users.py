from pydantic import BaseModel, Field 
from typing import List, Optional
from beanie import Document, Link, PydanticObjectId
from datetime import datetime

class User(Document):
    username: str = Field(min_length=3, max_length=50)
    password: str 
    email: Optional[str] 
    created: datetime = Field(default_factory=datetime.now)

    class Settings: 
        name="users"
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "John",
                "password": "password",
                "email": "john234@gmail.com"
            }
        }

class UserBase(BaseModel):
    id: PydanticObjectId
    username: str = Field(
        ...,
        min_length=3,
        max_length=15
    )
    password: str = Field(...)

class UserRegister(BaseModel):
    username: str 
    password: str 
    email: Optional[str] 

class UserLogin(BaseModel):
    username: str
    password: str

class CurrentUser(BaseModel):
    id: PydanticObjectId
    username: str
    email: str 

class UserList(BaseModel):
    users: List[CurrentUser]