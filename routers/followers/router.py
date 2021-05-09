from fastapi import APIRouter, Depends

from . import followers as follower_ops
from utils import common_user_auth, get_current_user
router = APIRouter()


@router.post("/set-follower", status_code=200, dependencies=[Depends(common_user_auth)])
def set_follower(user_email: str, current_user: dict = Depends(get_current_user)):
    return follower_ops.set_follower(user_email, current_user["email"])


@router.post("/delete-follower", status_code=200, dependencies=[Depends(common_user_auth)])
def delete_follower(follower_email: str, current_user: dict = Depends(get_current_user)):
    follower_ops.delete_follower(current_user["email"], follower_email)
