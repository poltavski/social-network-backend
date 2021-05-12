from fastapi import (
    APIRouter,
    Body,
    Form,
    Depends
)
from . import user as user_ops
from utils import common_user_auth

router = APIRouter()


@router.post("/create-user", status_code=200)
def create_user(user_data: dict = Body(...)):
    return user_ops.create_user(user_data)


@router.get("/user-info", status_code=200, dependencies=[Depends(common_user_auth)])
def get_user_details(email: str):
    return user_ops.get_user_info(email)


@router.post("/user-update-passwords", status_code=200, dependencies=[Depends(common_user_auth)])
def update_users_passwords():
    user_ops.update_users_passwords()
