from fastapi import (
    APIRouter,
    Body,
)
from . import user as user_ops

router = APIRouter()


@router.post("/create-user", status_code=200)
def create_user(user_data: dict = Body(...)):
    return user_ops.create_user(user_data)


@router.get("/user-info", status_code=200)
def get_user_details(email: str):
    return user_ops.get_user_info(email)
