from fastapi import APIRouter, Depends

from . import followers as follower_ops
from utils import get_current_user
from database.models import UserModel

router = APIRouter()


@router.post("/set-follower", status_code=200)
def set_follower(username: str, follower: UserModel = Depends(get_current_user)):
    return follower_ops.set_follower(username, follower)


@router.post("/delete-follower", status_code=200)
def delete_follower(username: str, follower: UserModel = Depends(get_current_user)):
    follower_ops.delete_follower(username, follower)
