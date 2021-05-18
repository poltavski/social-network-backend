import json
from fastapi import APIRouter, Body, Form, Depends
from fastapi_jwt_auth import AuthJWT
from . import user as user_ops
from utils import common_user_auth, get_current_user
from database.models import UserModel

router = APIRouter()


@router.get("/get-current-user", status_code=200)
def get_user_details(current_user: UserModel = Depends(get_current_user)):
    return user_ops.parse_user(current_user)


@router.post("/create-user", status_code=200)
def create_user(user_data: dict = Body(...), Authorize: AuthJWT = Depends()):
    return user_ops.create_user(user_data, Authorize)


@router.get("/user-info", status_code=200)
def get_user_details(email: str):
    return user_ops.get_user_info(email)


@router.get("/user-info-id", status_code=200)
def get_user_details(id: str):
    return user_ops.get_user_info_by_id(id)


@router.get("/search-user", status_code=200)
def get_user_match(user_info: str):
    return user_ops.search_user(user_info)


@router.post("/user-update-passwords", status_code=200)
def update_users_passwords():
    user_ops.update_users_passwords()
