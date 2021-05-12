from fastapi import APIRouter, Depends

from . import followers as follower_ops
from utils import common_user_auth, get_current_user
from database.models import UserModel

router = APIRouter()


@router.post("/set-follower", status_code=200)
def set_follower(user_email: str, follower: UserModel = Depends(get_current_user)):
    return follower_ops.set_follower(user_email, follower)


@router.post(
    "/delete-follower", status_code=200, dependencies=[Depends(common_user_auth)]
)
def delete_follower(user_email: str, follower: UserModel = Depends(get_current_user)):
    follower_ops.delete_follower(user_email, follower)
