from uuid import uuid4, UUID
import time
import os
from datetime import datetime

from peewee import fn
import aiofiles
from fastapi import HTTPException
from fastapi.responses import FileResponse

from database.models import UserModel, FollowerModel, PostModel, ImageModel
from database.database import db
from utils import query_fetchall, TIME_ALLOWED_CHANGE_MESSAGE_HOURS


def _is_allowed_time(created_time, hours=48) -> bool:
    # Cast to seconds.
    time_window = hours * 3600
    time_diff = (datetime.now() - created_time).seconds
    return time_diff < time_window


def is_editable_message(message: PostModel, user_id: UUID) -> bool:
    return (
            _is_allowed_time(message.create_time, TIME_ALLOWED_CHANGE_MESSAGE_HOURS)
            and message.user_id == user_id
    )


def get_feed_posts(email: str) -> list:
    user = UserModel.get_or_none(UserModel.email == email)
    subscriptions = (
        FollowerModel.select(
            fn.ARRAY_AGG(FollowerModel.user_id.distinct()).alias("subscription_list")
        )
        .where(FollowerModel.follower_id == user.id)
        .first()
    )
    subscription_list = subscriptions.subscription_list
    subscription_list.append(user.id)

    # TODO: Padding for create_time
    posts_query = query_fetchall(
        PostModel.select()
        .where(PostModel.user_id << subscription_list)
        .order_by(PostModel.create_time.desc())
        .limit(20)
    )

    posts = []
    for (
        uuid,
        user_id,
        image_id,
        content,
        create_time,
    ) in posts_query:
        # if image_id:
        #     get_image(image_id)
        posts.append(
            {
                "id": str(uuid),
                "user_id": user_id,
                "image_id": image_id,
                "content": content,
                "create_time": create_time,
            }
        )
    return posts


def create_post(user_id: UUID, post_data: dict) -> str:
    try:
        user = UserModel.get(UserModel.id == user_id)
        with db.atomic():
            post = PostModel.create(
                identifier=uuid4(),
                user_id=user.id,
                image_id=post_data.get("image_id"),
                content=post_data.get("content"),
                create_time=int(time.time()),
            )
            return str(post.id)
    except Exception as e:
        details = {"msg": "Failed to create a post.", "error": repr(e)}
        raise HTTPException(status_code=400, detail=details)


def change_post(post_id: UUID, new_post_data: dict) -> None:
    for key in new_post_data.keys():
        if key not in ["content", "image_id"]:
            details = {
                "post_id": str(post_id),
                "msg": "Only the 'content' and 'image_id' fields can be changed."
            }
            raise HTTPException(status_code=400, detail=details)

    post = PostModel.get_or_none(PostModel.id == post_id)
    if post is None:
        msg = f"Post Does not Exist: {post_id}"
        raise HTTPException(status_code=404, detail={"msg": msg})

    if not _is_allowed_time(post.create_time, TIME_ALLOWED_CHANGE_MESSAGE_HOURS):
        msg = f"Time to change the message is up."
        raise HTTPException(status_code=400, detail={"msg": msg})

    new_post_data.update(
        {
            "edited": True,
            "edit_time": int(time.time())
        }
    )
    try:
        with db.atomic():
            PostModel.update(new_post_data).where(PostModel.id == post_id).execute()
    except Exception as e:
        details = {"msg": "Failed to update a post.", "error": repr(e)}
        raise HTTPException(status_code=400, detail=details)


def delete_post(post_id) -> None:
    post = PostModel.get_or_none(PostModel.id == post_id)
    if post is None:
        msg = f"Post Does not Exist: {post_id}"
        raise HTTPException(status_code=404, detail={"msg": msg})
    if post.image_id:
        delete_image(post.image_id)

    with db.atomic():
        PostModel.delete().where(
            PostModel.id == post.id,
        ).execute()


def get_image(image_id: UUID):
    image = ImageModel.get_or_none(ImageModel.id == image_id)
    if image is None:
        detail = {"msg": f"Image Does not Exist: {image_id}"}
        raise HTTPException(status_code=404, detail=detail)

    file_name = f"./images/{image.id}.{image.format.split('/')[-1]}"
    if os.path.exists(file_name):
        return FileResponse(file_name, media_type=image.format)
    else:
        with db.atomic():
            ImageModel.delete().where(
                ImageModel.id == image.id,
            ).execute()
        return FileResponse("./images/404.jpeg", media_type="image/jpeg")


def delete_image(image_id: UUID):
    image = ImageModel.get_or_none(ImageModel.id == image_id)
    if image is None:
        detail = {"msg": f"Image Does not Exist: {image_id}"}
        raise HTTPException(status_code=404, detail=detail)

    file_name = f"./images/{image.id}.{image.format.split('/')[-1]}"
    if os.path.exists(file_name):
        os.remove(file_name)

    with db.atomic():
        ImageModel.delete().where(
            ImageModel.id == image.id,
        ).execute()
