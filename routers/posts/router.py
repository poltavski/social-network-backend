from fastapi import APIRouter, Body, Depends, UploadFile, File
from . import posts as post_ops

from database.models import UserModel, ImageModel
from database.database import db
from uuid import UUID
import time
import aiofiles
from utils import common_user_auth, get_current_user, check_user_access
from fastapi import HTTPException, File

router = APIRouter()


@router.post("/create-post", status_code=200, dependencies=[Depends(common_user_auth)])
def create_post(user_data: dict = Body(...), current_user: dict = Depends(get_current_user)):
    return post_ops.create_post(current_user["id"], user_data)


@router.post("/change-post", status_code=200, dependencies=[Depends(common_user_auth)])
def change_post(
    post_id: UUID,
    changed_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    if not check_user_access(
        current_user.get("id"),
        post_id,
        "post"
    ):
        detail = {
                "user_id": str(current_user.get("id")),
                "post_id": str(post_id),
                "msg": "Access denied.",  # noqa: E501
            }
        raise HTTPException(status_code=403, detail=detail)

    post_ops.change_post(post_id, changed_data)


@router.get("/get-feed", status_code=200, dependencies=[Depends(common_user_auth)])
def get_feed_posts(current_user: dict = Depends(get_current_user)):
    return post_ops.get_feed_posts(current_user.get("id"))


@router.post("/upload-image", status_code=200, dependencies=[Depends(common_user_auth)])
async def upload_image(
    image: UploadFile = File(...),
    is_profile: bool = Body(False),
    current_user: dict = Depends(get_current_user)
):
    user = UserModel.get_or_none(UserModel.id == current_user.get("id"))
    try:
        with db.atomic():
            image_model = ImageModel.create(
                user_id=user.id,
                format=image.content_type,
                is_profile=is_profile,
                create_time=int(time.time()),
            )
        out_file_path = (
            f"./images/{image_model.id}.{image.content_type.split('image/')[-1]}"
        )
        async with aiofiles.open(out_file_path, "wb") as out_file:
            content = await image.read()  # async read
            await out_file.write(content)  # async write
    except Exception as e:
        raise HTTPException(status_code=400, detail={"msg": repr(e)})


@router.get("/get-image", status_code=200)
async def get_image(image_id: UUID):
    return post_ops.get_image(image_id)


@router.post("/delete-image", status_code=200)
async def delete_image(image_id: UUID, current_user: dict = Depends(get_current_user)):
    if not check_user_access(
        current_user.get("id"),
        image_id,
        "image"
    ):
        detail = {
                "user_id": str(current_user.get("id")),
                "post_id": str(image_id),
                "msg": "Access denied.",  # noqa: E501
            }
        raise HTTPException(status_code=403, detail=detail)
    return post_ops.delete_image(image_id)
