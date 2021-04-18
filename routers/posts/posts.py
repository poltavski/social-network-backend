from database.models import UserModel, FollowerModel, PostModel
from database.database import db
from uuid import uuid4
import time

from fastapi import HTTPException


def get_feed_posts(email):
    user = UserModel.get_or_none(UserModel.email == email)
    subscriptions = (
        FollowerModel.select(FollowerModel.user_id.distinct())
        .where(FollowerModel.follower_id == user.id)
    )
    # TODO: Padding for create_time
    posts = list(
        PostModel.select(
            PostModel.id,
            PostModel.user_id,
            PostModel.image_id,
            PostModel.content,
            PostModel.create_time
        )
        .from_(subscriptions)
        .where(PostModel.user_id == subscriptions.c.user_id)
        .order_by(PostModel.create_time.desc())
        .limit(20)
        .namedtuples()
        .iterator()
    )
    return posts


def create_post(post_data):
    try:
        user = UserModel.get(UserModel.email == post_data.get("email"))
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
        details = {
            "msg": "Failed to create a post.",
            "error": repr(e)
        }
        raise HTTPException(status_code=400, detail=details)


def delete_post(post_id):
    post = PostModel.get_or_none(PostModel.id == post_id)
    if post is None:
        msg = f"Post Does not Exist: {post_id}"
        raise HTTPException(status_code=404, detail={"msg": msg})

    with db.atomic():
        PostModel.delete().where(
            PostModel.id == post.id,
        ).execute()
