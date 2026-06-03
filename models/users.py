from pydantic import BaseModel, Field 
from typing import List, Optional

from models.cars import PyObjectId 

class UserBase(BaseModel):
    id: Optional[PyObjectId] =  Field(alias="_id", default=None)
    username: str = Field(
        ...,
        min_length=3,
        max_length=15
    )
    password: str = Field(...)

class UserLogin(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

class CurrentUser(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(
        ...,
        min_length=3,
        max_length=15
    )

class UserList(BaseModel):
    users: List[CurrentUser]