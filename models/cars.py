from typing import Optional, Annotated, List 
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator, field_validator
from beanie import Document, Link, PydanticObjectId
from datetime import datetime
from models.users import User  

class Car(Document):
    brand: str 
    make: str | int
    year: int 
    cm3: int 
    km: int 
    price: int 
    picture_url: Optional[str] = None 
    description: Optional[str] = None 
    pros: List[str] = []
    cons: List[str] = []
    date: datetime = datetime.now() 
    user: Optional[Link[User]] = None 

    @field_validator("make", mode="before")
    @classmethod
    def convert_make_to_str(cls, value):
        return str(value)

    class Settings:
        name="cars"
   
    class Config:
        json_schema_extra={
            "example":{
                "brand": "Audi",
                "make": "A4",
                "year": 2020,
                "cm3": 2000,
                "km": 50000, 
                "price": 100000
            }
        }


class updateCar(BaseModel):
    price: Optional[float] = None 
    description: Optional[str] = None 
    pros: Optional[List[str]] = None 
    cons: Optional[List[str]] = None 

class CarCollection(BaseModel):
    cars: List[Car]

class CarCollectionPagination(CarCollection):
    page: int = Field(ge=1, default=1)
    has_more: bool 