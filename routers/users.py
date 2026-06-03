import json 
import uuid 
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from authentication import AuthHandler, auth_handler
from models.users import UserBase, UserLogin, CurrentUser, UserList
from bson import ObjectId

router = APIRouter()
auth_handler = AuthHandler()

@router.post("/register", response_description="Register a new user", status_code=201)
async def register_user(request: Request, newUser: UserLogin = Body(...)) -> UserBase:
    users = request.app.db["users"]

    newUser.password = auth_handler.get_hashed_password(newUser.password)
    new_user = newUser.model_dump()

    
    if (await users.find_one({"username": newUser.username}) is not None):
        raise HTTPException(status_code=409, detail=f"Username {newUser.username} is already taken")
    new_user = await users.insert_one(new_user)
    created_user = await users.find_one({"_id": new_user.inserted_id})
    return created_user 

@router.post("/login", response_description="Login a user")
async def login_user(request: Request, loginUser: UserLogin = Body(...)):
    users = request.app.db["users"]

    user = await users.find_one({"username": loginUser.username})
    if (user is None) or (not auth_handler.verify_password(loginUser.password, user["password"])):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = auth_handler.encode_token(str(user["_id"]), user["username"])
    response = JSONResponse(
        content={
            "token": token,
            "username": user["username"]
        }
    )
    return response 

@router.get(
    "/me",
    response_description="Logged in user data",
    response_model=CurrentUser
)
async def me(
 request: Request,
 user_data=Depends(auth_handler.auth_wrapper)
):
    users = request.app.db["users"]
    currentUser = await users.find_one(
    {"_id": ObjectId(user_data["user_id"])}
    )
    return currentUser