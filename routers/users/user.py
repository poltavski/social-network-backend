from collections import namedtuple
from database.models import UserModel, FollowerModel
from database.database import db
import time
from datetime import timedelta
from peewee import fn
from fastapi import HTTPException
from passlib.context import CryptContext

from utils import UserAuth, login_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_password_hash(password):
    return pwd_context.hash(password)


def get_followers_info(user_id):
    followers = (
        FollowerModel.select(
            fn.COUNT(FollowerModel.follower_id.distinct()).alias("num_of_followers")
        )
        .where(FollowerModel.user_id == user_id)
        .first()
    )

    subscriptions = (
        FollowerModel.select(
            fn.COUNT(FollowerModel.user_id.distinct()).alias("num_of_subscriptions")
        )
        .where(FollowerModel.follower_id == user_id)
        .first()
    )
    return {
        "num_of_followers": followers.num_of_followers,
        "num_of_subscriptions": subscriptions.num_of_subscriptions,
    }


def get_user_info(user_email):
    user = UserModel.get_or_none(UserModel.email == user_email)
    if user is None:
        detail = {"msg": f"User Does not Exist: {user_email}"}
        raise HTTPException(status_code=404, detail=detail)

    user_info = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": f"{user.first_name} {user.last_name}",
        "create_time": user.create_time,
        "disabled": user.disabled,
    }
    user_info.update(get_followers_info(user.id))
    return user_info


def create_user(user_data, Authorize):
    try:
        with db.atomic():
            UserModel.create(
                username=user_data["username"],
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                description=user_data.get("description"),
                password_hash=_get_password_hash(user_data["password"]),
                create_time=int(time.time()),
            )
        struct = namedtuple('UserAuth', 'username password')
        user_data = struct(username=user_data["email"], password=user_data["password"])
        login_user(user_data, Authorize)
    except Exception as e:
        details = {"msg": "Failed to create a user.", "error": repr(e)}
        raise HTTPException(status_code=400, detail=details)


def update_users_passwords():
    users = UserModel.select().iterator()
    modified_users = []
    for user in users:
        user.password_hash = _get_password_hash(user.password_hash)
        modified_users.append(user)
    UserModel.bulk_update(modified_users, fields=["password_hash"])
