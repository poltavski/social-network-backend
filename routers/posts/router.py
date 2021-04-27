from fastapi import (
    APIRouter,
    Body,
    UploadFile,
    File
)
from . import posts as post_ops
import aiofiles

from database.models import UserModel, ImageModel
from database.database import db
from uuid import uuid4
import time
from peewee import fn
import aiofiles
from utils import query_fetchall
from fastapi import HTTPException

router = APIRouter()


@router.post("/create-post", status_code=200)
def create_post(user_data: dict = Body(...)):
    return post_ops.create_post(user_data)


@router.get("/get-feed", status_code=200)
def get_feed_posts(email: str):
    return post_ops.get_feed_posts(email)


@router.post("/upload-image", status_code=200)
async def upload_image(
        image: UploadFile = File(...),
        user_email: str = Body(...),
        is_profile: bool = Body(False),
):
    user = UserModel.get_or_none(UserModel.email == user_email)
    if user is None:
        detail = {"msg": f"User Does not Exist: {user_email}"}
        raise HTTPException(status_code=404, detail=detail)

    try:
        with db.atomic():
            image_model = ImageModel.create(
                user_id=user.id,
                format=image.content_type,
                is_profile=is_profile,
                create_time=int(time.time()),
            )
        out_file_path = f"./images/{image_model.id}.{image.content_type.split('image/')[-1]}"
        async with aiofiles.open(out_file_path, 'wb') as out_file:
            content = await image.read()  # async read
            await out_file.write(content)  # async write
    except Exception as e:
        raise HTTPException(status_code=400, detail={"msg": repr(e)})
    return None