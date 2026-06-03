from typing import Optional, Annotated, List 
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator, field_validator

PyObjectId = Annotated[str, BeforeValidator(str)]

class Car(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    brand: str = Field(...)
    make: str | int = Field(...)
    year: int = Field(..., gt=1900, lt=2030)
    cm3: int = Field(..., gt=0, lt=10_000)
    km: int = Field(..., gt=0, lt=2_000_000)
    price: int = Field(..., gt=0, lt=1_000_000)
    picture_url: Optional[str] = Field(None)
    user_id: str = Field(...)
    
    @field_validator('brand')
    @classmethod 
    def validate_brand(cls, value: str) -> str:
        return value.title()
    
    @field_validator("make")
    @classmethod
    def validate_make(cls, value: str | int) -> str:
        if isinstance(value, int):
            return str(value)
        return value.title()
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
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
    )

class updateCar(BaseModel):
    brand: Optional[str] = Field(None)
    make: Optional[str] = Field(None)
    year: Optional[int] = Field(None, gt=1970, lt=2025)
    cm3: Optional[int] = Field(None, gt=0, lt=5000)
    km: Optional[int] = Field(None, gt=0, lt=500 * 1000)
    price: Optional[int] = Field(None, gt=0, lt=100 * 1000)

class CarCollection(BaseModel):
    cars: List[Car]

class CarCollectionPagination(CarCollection):
    page: int = Field(ge=1, default=1)
    has_more: bool 