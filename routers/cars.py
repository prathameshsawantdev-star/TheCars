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
 Depends, 
 BackgroundTasks
)
from pydantic.v1 import ValidationError 
from bson.objectid import ObjectId
from models.cars import Car as CarModel, CarCollection, CarCollectionPagination, updateCar as updateCarModel 
from models.users import User
from authentication import auth_handler
from pymongo import ReturnDocument
import cloudinary 
from cloudinary import uploader 
from config import BaseConfig
from beanie import PydanticObjectId, WriteRules
from background import generate_ai_opinion 
import resend 
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
 status_code=status.HTTP_201_CREATED,

             )
async def create_car_with_picture(
    request: Request,
    background_task: BackgroundTasks ,
    brand: str = Form("brand"),
    make: str | int = Form("make"),
    year: int = Form("year"),
    cm3: int = Form("cm3"),
    km: int = Form("km"),
    price: int = Form("price"),
    picture: UploadFile | None = Form(None),
    pictureName: str | None = Form(None),
    user_data=Depends(auth_handler.auth_wrapper),
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
        pictureFile, crop="fill", width=800, folder="FARM", gravity="auto"
    )
    picture_url = cloudinary_image["url"]
    user = await User.get(user_data["id"])
    car = CarModel(
        brand=brand,
        make=make,
        year=year,
        cm3=cm3,
        km=km,
        price=price,
        picture_url=picture_url,
        user=user
    )
    await car.insert(link_rule=WriteRules.WRITE)
    background_task.add_task(
        generate_ai_opinion,
        id=str(car.id),
        brand=brand,
        make=str(make),
        year=year,
        picture_url=picture_url,
    )

    return car



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
    print("getting car info")
    cars = (
        await CarModel.find_all()
            .sort(-CarModel.id)
            .skip((page - 1) * limit)
            .limit(limit)
            .to_list()
    )
    total_documents = await CarModel.count()
    print("total docs", total_documents)
    has_more = page * limit < total_documents 
    return CarCollectionPagination(cars=cars, page=page, has_more=has_more)

@router.get(
    "/{id}",
    response_description="Find a car by id",
    response_model=CarModel,
    response_model_by_alias=True
    )
async def find_car(id: str, request: Request):
    try:
        id = ObjectId(id)
    except Exception:
       raise HTTPException(status_code=404, detail=f"{id} is not a valid ObjectId")
    
    car = await CarModel.get(id)
    if car is None: 
        raise HTTPException(status_code=404, detail=f"Car with id ${id} not Found")

@router.put(
    "/{id}",
    response_description="Update car details",
    response_model=CarModel,
    response_model_by_alias=True
    )
async def update_car(id: str, 
                     request: Request, 
                     cardata: updateCarModel = Body(...),
                     user = Depends(auth_handler.auth_wrapper)
                     ):

    try:
        id = ObjectId(id)
    except Exception:
         raise HTTPException(status_code=404, detail=f"{id} is not a valid ObjectId")
    car = await CarModel.get(id)
    if not car:
        raise HTTPException(
            status_code=404,
            detail="Car not Found"
        )
    updated_car = {k: v for k, v in cardata.model_dump().items() if v is not None}
    return await car.set(updated_car)
    
@router.delete(
    "/{id}",
    response_description="Delete a car"
    )
async def delete_car(id: str, request: Request, user = Depends(auth_handler.auth_wrapper)):
    try:
        id = ObjectId(id)
    except Exception:
         raise HTTPException(status_code=404, detail=f"{id} is not a valid ObjectId")
    
    car = await CarModel.get(id)
    if car is not None: 
        raise HTTPException(status_code=404, detail="Car not found")
    await car.delete()