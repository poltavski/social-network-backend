from fastapi import APIRouter

from . import followers as follower_ops
router = APIRouter()


@router.post("/set-follower", status_code=200)
def set_follower(user_email: str, follower_email: str):
    return follower_ops.set_follower(user_email, follower_email)


@router.post("/delete-follower", status_code=200)
def delete_follower(user_email: str, follower_email: str):
    follower_ops.delete_follower(user_email, follower_email)
