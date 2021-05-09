from fastapi import APIRouter, Depends

from . import followers as follower_ops
from utils import common_user_auth
router = APIRouter()


@router.post("/set-follower", status_code=200, dependencies=[Depends(common_user_auth)])
def set_follower(user_email: str, follower_email: str):
    return follower_ops.set_follower(user_email, follower_email)


@router.post("/delete-follower", status_code=200, dependencies=[Depends(common_user_auth)])
def delete_follower(user_email: str, follower_email: str):
    follower_ops.delete_follower(user_email, follower_email)
