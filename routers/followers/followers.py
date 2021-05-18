from database.models import UserModel, FollowerModel
from database.database import db
from utils import get_user, get_user_by_id

import time
from fastapi import HTTPException


def set_follower(username, follower):
    user = UserModel.get_or_none(UserModel.username == username)
    if user is None:
        msg = f"User Does not Exist: {username}"
        raise HTTPException(status_code=404, detail={"msg": msg})
    if user.id == follower.id:
        raise HTTPException(
            status_code=404,
            detail={
                "msg": "It is forbidden to use the same user for 'user' and 'follower'"
            },
        )

    follower_check = FollowerModel.get_or_none(
        FollowerModel.user_id == user.id, FollowerModel.follower_id == follower.id
    )
    if follower_check is None:
        with db.atomic():
            FollowerModel.create(
                user_id=user.id, follower_id=follower.id, create_time=int(time.time())
            )


def delete_follower(username, follower):
    user = UserModel.get_or_none(UserModel.username == username)
    if user is None:
        msg = f"User Does not Exist: {username}"
        raise HTTPException(status_code=404, detail={"msg": msg})
    with db.atomic():
        FollowerModel.delete().where(
            FollowerModel.user_id == user.id, FollowerModel.follower_id == follower.id
        ).execute()
