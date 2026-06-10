import json 
import uuid 
from fastapi import APIRouter, Body, Depends, HTTPException, Request, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from authentication import AuthHandler, auth_handler
from models.users import User, UserBase, UserLogin, CurrentUser, UserRegister, UserList
from bson import ObjectId
router = APIRouter()
auth_handler = AuthHandler()

@router.post("/register", response_description="Register a new user", response_model=CurrentUser, status_code=201)
async def register_user(request: Request, newUser: UserRegister  = Body(...)) -> UserBase:

    newUser.password = auth_handler.get_hashed_password(newUser.password)
    query = {
        "$or": [{
            "username": newUser.username,
            "email": newUser.email 
        }]
    }
    existing_user = await User.find_one(query)
    if(existing_user is not None):
        raise HTTPException(
            status_code=409,
            detail=f"Username = {newUser.username} or Email = {newUser.email} already exists"
        )
    
    user = await User(**newUser.model_dump()).save()
    return user

@router.post("/login", response_description="Login a user")
async def login_user(request: Request,
                     background_tasks: BackgroundTasks,
                      loginUser: UserLogin = Body(...)):
    user = await User.find_one(
        User.username == loginUser.username 
    )

    if (user is None) or (not auth_handler.verify_password(loginUser.password, user.password)):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = auth_handler.encode_token(str(user.id), user.username)
    response = JSONResponse(
        content={
            "token": token,
            "username": user.username
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
    currentUser = await User.get(
    {"_id": ObjectId(user_data["id"])}
    )
    return currentUser