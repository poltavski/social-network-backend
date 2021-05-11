from database.models import UserModel, FollowerModel
from database.database import db
import time
from datetime import timedelta

from peewee import fn
from fastapi import HTTPException
from passlib.context import CryptContext

from utils import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

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
        "disabled": user.disabled
    }
    user_info.update(get_followers_info(user.id))
    return user_info


def create_user(user_data):
    try:
        with db.atomic():
            user = UserModel.create(
                username=user_data.get("username"),
                email=user_data.get("email"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                description=user_data.get("description"),
                password_hash=_get_password_hash(user_data.get("password")),
                create_time=int(time.time()),
            )

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )
            return {"user_id": str(user.id), "access_token": access_token, "token_type": "bearer"}
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
