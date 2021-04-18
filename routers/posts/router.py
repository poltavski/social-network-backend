from fastapi import (
    APIRouter,
    Body,
)
from . import posts as post_ops

router = APIRouter()


@router.post("/create-post", status_code=200)
def create_post(user_data: dict = Body(...)):
    return post_ops.create_post(user_data)


@router.get("/get-feed", status_code=200)
def get_feed_posts(email: str):
    return post_ops.get_feed_posts(email)

