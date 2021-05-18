from database.models import UserModel, FollowerModel
from database.database import db
from utils import get_user

import time
from fastapi import HTTPException


def set_follower(user_email, follower):
    if user_email == follower.email:
        raise HTTPException(
            status_code=404,
            detail={
                "msg": "It is forbidden to use the same user for 'user' and 'follower'"
            },
        )
    user = get_user(user_email)
    follower_check = FollowerModel.get_or_none(
        FollowerModel.user_id == user.id, FollowerModel.follower_id == follower.id
    )
    if follower_check is None:
        with db.atomic():
            FollowerModel.create(
                user_id=user.id, follower_id=follower.id, create_time=int(time.time())
            )


def delete_follower(user_email, follower):
    user = get_user(user_email)
    with db.atomic():
        FollowerModel.delete().where(
            FollowerModel.user_id == user.id, FollowerModel.follower_id == follower.id
        ).execute()
