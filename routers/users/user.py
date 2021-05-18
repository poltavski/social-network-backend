from collections import namedtuple
from database.models import ImageModel, UserModel, FollowerModel
from database.database import db
import time
from datetime import timedelta
from peewee import fn
from fastapi import HTTPException
from passlib.context import CryptContext

from utils import login_user, get_user, get_user_by_id

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


def get_profile_image(user_id):
    profile_image = (
        ImageModel.select(ImageModel.id)
        .where((ImageModel.user_id == user_id) & ImageModel.is_profile)
        .first()
    )
    return {"profile_image": profile_image.id if profile_image else None}


def parse_user(user):
    user_info = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "description": user.description,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": f"{user.first_name} {user.last_name}",
        "create_time": user.create_time,
        "disabled": user.disabled,
    }
    user_info.update(get_followers_info(user.id))
    user_info.update(get_profile_image(user.id))

    return user_info


def get_user_info(user_email):
    user = get_user(user_email)
    return parse_user(user)


def get_user_info_by_id(user_id):
    user = get_user_by_id(user_id)
    return parse_user(user)


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
        struct = namedtuple("UserAuth", "username password")
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


def search_user(user_info):
    pass
    # purify
    user_info = user_info.lower()
    # fetch users info
    users = UserModel.select().namedtuples()
    search_vocab = {}
    search_response = {}
    for user in users:
        # fill search vocab dict
        user_id = str(user.id)
        search_vocab[user_id] = {
            "username": user.username,
            "name": f"{user.first_name} {user.last_name}",
        }
        # Search for username and name appearances
        match_cases_username = search_vocab[user_id]["username"].lower().find(user_info)
        match_cases_name = search_vocab[user_id]["name"].lower().find(user_info)
        # If found, push results to search response
        if match_cases_username >= 0 or match_cases_name >= 0:
            search_response.update({user_id: search_vocab[user_id]})
    # sort values
    search_response = dict(
        sorted(search_response.items(), key=lambda item: item[1]["username"])
    )
    return search_response
