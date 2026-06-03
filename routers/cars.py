from pydoc import doc



from fastapi import (
 APIRouter,
 Body,
 File,
 Form,
 HTTPException,
 Request,
 UploadFile,
 status,
 Depends
)
from pydantic.v1 import ValidationError 
from bson.objectid import ObjectId
from models.cars import Car as CarModel, CarCollection, CarCollectionPagination, updateCar as updateCarModel 
from authentication import auth_handler
from pymongo import ReturnDocument
import cloudinary 
from cloudinary import uploader 
from config import BaseConfig

settings = BaseConfig()
router = APIRouter()

CARS_PER_PAGE = 5

cloudinary.config(
 cloud_name=settings.CLOUDINARY_CLOUD_NAME,
 api_key=settings.CLOUDINARY_API_KEY,
 api_secret=settings.CLOUDINARY_SECRET_KEY,
)

@router.get("/randomcar", response_description="Get a random car", response_model=CarModel, response_model_by_alias=True)
async def random_car(request: Request):
    cars = request.app.db["cars"]
    random_car = await cars.find_one()
    if random_car:
        return print(random_car)
    else:
        raise HTTPException(status_code=404, detail="No cars found")
    
@router.post("/",
 response_description="Add new car with picture",
 response_model=CarModel,
 status_code=status.HTTP_201_CREATED
             )
async def create_car_with_picture(
    request: Request,
    brand: str = Form("brand"),
    make: str | int = Form("make"),
    year: int = Form("year"),
    cm3: int = Form("cm3"),
    km: int = Form("km"),
    price: int = Form("price"),
    picture: UploadFile | None = Form(None),
    pictureName: str | None = Form(None),
    user = Depends(auth_handler.auth_wrapper)
):
    print(cloudinary.config().cloud_name)
    print(cloudinary.config().api_key)
    pictureFile = None
    if picture is not None:
        pictureFile = picture.file

    elif pictureName is not None:
        pictureFile = open(
        f"./uploads/{pictureName}",
        "rb"
        )

    else:
        raise HTTPException(
        status_code=400,
        detail="Either picture or pictureName is required"
    )
    print("picture type:", type(pictureFile))
    cloudinary_image = cloudinary.uploader.upload(
        pictureFile, crop="fill", width=800
    )
    picture_url = cloudinary_image["url"]
    car = CarModel(
        brand=brand,
        make=make,
        year=year,
        cm3=cm3,
        km=km,
        price=price,
        picture_url=picture_url,
        user_id= user["user_id"]
    )
    cars = request.app.db["cars"]
    document = car.model_dump(
        by_alias=True,
        exclude={"id"}
    )
    inserted = await cars.insert_one(document)
    return await cars.find_one({"_id": inserted.inserted_id})


# @router.post(
#     "/",
#     response_description="Add new car",
#     response_model=CarModel,
#     status_code=status.HTTP_201_CREATED,
#     response_model_by_alias=True 
#     )
# async def create_car(request: Request, car: CarModel = Body(...)):
#     cars = request.app.db["cars"]
#     document = car.model_dump(
#         by_alias=True,
#         exclude={"id"}
#     )
#     inserted = await cars.insert_one(document)
#     return await cars.find_one({"_id": inserted.inserted_id})

@router.get(
    "/",
    response_description="List all cars",
    response_model=CarCollectionPagination,
    response_model_by_alias=True,
    )
async def list_cars(request: Request, page: int = 1, limit: int = CARS_PER_PAGE):
    cars = request.app.db["cars"]
    results = []
    cursor = cars.find().limit(limit).skip((page - 1) * limit)
    total_documents = await cars.count_documents({})
    has_more = page * limit < total_documents 
    async for doc in cursor:
        results.append(CarModel.model_validate(doc))
    return CarCollectionPagination(cars=results, page=page, has_more=has_more)

@router.get(
    "/{id}",
    response_description="Find a car by id",
    response_model=CarModel,
    response_model_by_alias=True
    )
async def find_car(id: str, request: Request):
    cars = request.app.db["cars"]

    try:
        id = ObjectId(id)
    except Exception:
       raise HTTPException(status_code=404, detail=f"{id} is not a valid ObjectId")
    
    if (car := await cars.find_one({"_id": id})):
        return CarModel.model_validate(car)
    else: 
        raise HTTPException(status_code=404, detail=f"Car with {id} not found")

@router.put(
    "/{id}",
    response_description="Update car details",
    response_model=CarModel,
    response_model_by_alias=True
    )
async def update_car(id: str, 
                     request: Request, 
                     car: updateCarModel = Body(...),
                     user = Depends(auth_handler.auth_wrapper)
                     ):
    cars = request.app.db["cars"]

    try:
        id = ObjectId(id)
    except Exception:
         raise HTTPException(status_code=404, detail=f"{id} is not a valid ObjectId")
    
    updatedCar = {
        k: v 
        for k, v in car.model_dump(
            by_alias=True,
            exclude={"id"}
        ).items() if v is not None 
    }

    if len(updatedCar) >= 1:
        cars = request.app.db["cars"]

        update_result = await cars.find_one_and_update(
            {"_id": id},
            {"$set": updatedCar},
            return_document=ReturnDocument.AFTER
        )

        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Car {id} not found")

    if(existingCar := await cars.find_one({"_id": id})):
        return existingCar
    else:
        raise HTTPException(status_code=404, detail=f"Car {id} not found")
    
@router.delete(
    "/{id}",
    response_description="Delete a car"
    )
async def delete_car(id: str, request: Request, user = Depends(auth_handler.auth_wrapper)):
    cars = request.app.db["cars"]

    try:
        id = ObjectId(id)
    except Exception:
         raise HTTPException(status_code=404, detail=f"{id} is not a valid ObjectId")
    
    delete_result = await cars.delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=404, detail=f"Car {id} not found")
    
@router.get("/get/counts", response_description="Get the total count of cars")
async def count_cars(request: Request):
    cars = request.app.db["cars"]
    total_count = await cars.count_documents({})
    return {"total_count": total_count}

@router.get("/test/invalid", response_description="Test cars with invalid schema")
async def test_invalid_cars(request: Request):
    cars = request.app.db["cars"]
    invalid_docs = []
    valid_count = 0

    cursor = cars.find()

    async for doc in cursor:
        try: 
            CarModel.model_validate(doc)
            valid_count += 1
        except Exception as e:
            await cars.delete_one({"_id": doc["_id"]})
            invalid_docs.append(str(doc["_id"]))

    return {
        "valid_count": valid_count,
        "invalid_count": len(invalid_docs),
        "invalid_documents": invalid_docs
    }

