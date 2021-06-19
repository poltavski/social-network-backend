from fastapi import APIRouter, Depends

from . import followers as follower_ops
from utils import get_current_user
from database.models import UserModel
from database.database import get_db

router = APIRouter()


@router.post("/set-follower", status_code=200, dependencies=[Depends(get_db)])
def set_follower(username: str, follower: UserModel = Depends(get_current_user)):
    return follower_ops.set_follower(username, follower)


@router.post("/delete-follower", status_code=200, dependencies=[Depends(get_db)])
def delete_follower(username: str, follower: UserModel = Depends(get_current_user)):
    follower_ops.delete_follower(username, follower)
