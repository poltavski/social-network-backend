from uuid import uuid4, UUID
import time
import os
from datetime import datetime

from peewee import fn
from fastapi import HTTPException
from fastapi.responses import FileResponse

from database.models import UserModel, FollowerModel, PostModel, ImageModel
from database.database import db
from utils import query_fetchall, TIME_ALLOWED_CHANGE_MESSAGE_HOURS, VISIBILITY_TYPES


def _time_from_now(created_time):
    if isinstance(created_time, int):
        created_time = datetime.fromtimestamp(created_time)
    time_diff = datetime.now() - created_time
    days = time_diff.days
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds // 60) % 60
    if days > 0:
        time_res = f"{days} days ago"
    elif hours > 0:
        time_res = f"{hours} hours ago"
    else:
        time_res = f"{minutes} minutes ago"
    return time_res


def _is_change_allowed_time(created_time, hours=48) -> bool:
    # Cast to seconds.
    time_window = hours * 3600
    if isinstance(created_time, int):
        created_time = datetime.fromtimestamp(created_time)
    time_diff = (datetime.now() - created_time).total_seconds()
    return time_diff < time_window


def get_profile_image(user_id):
    profile_image = (
        ImageModel.select(ImageModel.id)
        .where((ImageModel.user_id == user_id) & ImageModel.is_profile)
        .first()
    )
    return profile_image.id if profile_image else None


def is_editable_post(post_id: UUID, user_id: UUID, create_time: int) -> bool:
    return (
        _is_change_allowed_time(create_time, TIME_ALLOWED_CHANGE_MESSAGE_HOURS)
        and post_id == user_id
    )


def get_feed_posts(user: UserModel) -> list:
    subscriptions_list = (
        FollowerModel.select(
            fn.ARRAY_AGG(FollowerModel.user_id.distinct()).alias("subscriptions")
        )
        .where(FollowerModel.follower_id == user.id)
        .first()
    ).subscriptions

    followers_list = (
        FollowerModel.select(
            fn.ARRAY_AGG(FollowerModel.follower_id.distinct()).alias("followers")
        )
        .where(FollowerModel.user_id == user.id)
        .first()
    ).followers

    # Add user itself for consistency.
    if subscriptions_list:
        subscriptions_list.append(user.id)
    else:
        subscriptions_list = [user.id]

    # TODO: Padding for create_time
    if not followers_list:
        followers_list = []
    where_criteria = [
        PostModel.user_id << subscriptions_list,
        (
            (PostModel.user_id == user.id)
            | (PostModel.visibility == "public")
            | (
                (PostModel.visibility == "friends")
                & (PostModel.user_id << followers_list)
            )
        ),
    ]
    select_criteria = [
        PostModel.id,
        PostModel.user_id,
        PostModel.image_id,
        PostModel.content,
        PostModel.create_time,
        PostModel.edited,
        PostModel.edit_time,
        PostModel.likes,
        UserModel.username,
        UserModel.first_name,
        UserModel.last_name,
    ]
    posts_query = (
        PostModel.select(*select_criteria)
        .join(UserModel)
        .where(*where_criteria)
        .order_by(PostModel.create_time.desc())
        .limit(50)
    )
    posts_query = query_fetchall(posts_query)

    posts = []
    for (
        uuid,
        post_user_id,
        image_id,
        content,
        create_time,
        edited,
        edit_time,
        likes,
        username,
        first_name,
        last_name,
    ) in posts_query:
        posts.append(
            {
                "id": str(uuid),
                "user_id": post_user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "profile_image_id": get_profile_image(post_user_id),
                "image_id": image_id,
                "content": content,
                "create_time": create_time,
                "time_from_now": _time_from_now(create_time),
                "likes": len(likes) if likes else 0,
                "edited": edited,
                "edit_time": edit_time,
                "editable": is_editable_post(post_user_id, user.id, create_time),
                "removable": post_user_id == user.id,
            }
        )
    return posts


def create_post(user: UserModel, post_data: dict) -> dict:
    try:
        with db.atomic():
            visibility = post_data.get("visibility")
            post = PostModel.create(
                identifier=uuid4(),
                user_id=user.id,
                image_id=post_data.get("image_id"),
                content=post_data.get("content"),
                create_time=int(time.time()),
                visibility=visibility if visibility in VISIBILITY_TYPES else "public",
            )
            return {
                "id": str(post.id),
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_image_id": get_profile_image(user.id),
                "image_id": post.image_id.id if post.image_id else None,
                "content": post.content,
                "create_time": post.create_time,
                "time_from_now": _time_from_now(post.create_time),
                "likes": len(post.likes) if post.likes else 0,
                "edited": post.edited,
                "edit_time": post.edit_time,
                "editable": is_editable_post(user.id, user.id, post.create_time),
                "removable": True,
            }
    except Exception as e:
        details = {"msg": "Failed to create a post.", "error": repr(e)}
        raise HTTPException(status_code=400, detail=details)


def change_post(post_id: UUID, new_post_data: dict) -> None:
    for key in new_post_data.keys():
        if key not in ["content", "image_id"]:
            details = {
                "post_id": str(post_id),
                "msg": "Only the 'content' and 'image_id' fields can be changed.",
            }
            raise HTTPException(status_code=400, detail=details)

    post = PostModel.get_or_none(PostModel.id == post_id)
    if post is None:
        msg = f"Post Does not Exist: {post_id}"
        raise HTTPException(status_code=404, detail={"msg": msg})

    if not _is_change_allowed_time(post.create_time, TIME_ALLOWED_CHANGE_MESSAGE_HOURS):
        msg = f"Time to change the message is up."
        raise HTTPException(status_code=400, detail={"msg": msg})

    new_post_data.update({"edited": True, "edit_time": int(time.time())})
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

    with db.atomic():
        PostModel.delete().where(
            PostModel.id == post.id,
        ).execute()

    if post.image_id:
        delete_image(post.image_id)


def get_image(image_id: UUID, is_profile: bool = False):
    image = ImageModel.get_or_none(ImageModel.id == image_id) if image_id else None

    file_name = f"./images/{image.id}.{image.format.split('/')[-1]}" if image else None
    if file_name and os.path.exists(file_name):
        return FileResponse(file_name, media_type=image.format)
    else:
        with db.atomic():
            try:
                ImageModel.delete().where(
                    ImageModel.id == image.id,
                ).execute()
            except:
                pass
        if is_profile:
            not_found_image = "./images/profile.jpeg"
        else:
            not_found_image = "./images/404.jpeg"

        return FileResponse(not_found_image, media_type="image/jpeg")


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


def change_likes(user, post_id):
    post = PostModel.get_or_none(PostModel.id == post_id)
    if post is None:
        detail = {"msg": f"Image Does not Exist: {post_id}"}
        raise HTTPException(status_code=404, detail=detail)

    likes = post.likes if post.likes else []
    user_id = str(user.id)
    if user_id in likes:
        likes.remove(user_id)
        if not likes:
            # Empty list
            likes = None
    else:
        likes.append(user_id)

    with db.atomic():
        PostModel.update(likes=likes).where(PostModel.id == post_id).execute()
    return len(likes) if likes else 0
