from fastapi import APIRouter, Body, Depends, UploadFile, File
from . import posts as post_ops

from database.models import UserModel, ImageModel
from database.database import db
from uuid import UUID
import time
import aiofiles
from utils import get_current_user, check_user_access
from database.models import UserModel
from database.database import get_db

from fastapi import HTTPException, File

router = APIRouter()


@router.post("/create-post", status_code=200, dependencies=[Depends(get_db)])
def create_post(
    post_data: dict = Body(...), current_user: UserModel = Depends(get_current_user)
):
    return post_ops.create_post(current_user, post_data)


@router.post("/change-post", status_code=200, dependencies=[Depends(get_db)])
def change_post(
    post_id: UUID,
    changed_data: dict = Body(...),
    current_user: UserModel = Depends(get_current_user),
):
    if not check_user_access(current_user.id, post_id, "post"):
        detail = {
            "user_id": str(current_user.id),
            "post_id": str(post_id),
            "msg": "Access denied.",  # noqa: E501
        }
        raise HTTPException(status_code=403, detail=detail)

    post_ops.change_post(post_id, changed_data)


@router.get("/change-likes", status_code=200, dependencies=[Depends(get_db)])
def change_post(
    post_id: UUID,
    current_user: UserModel = Depends(get_current_user),
):
    return post_ops.change_likes(current_user, post_id)


@router.get("/get-feed", status_code=200, dependencies=[Depends(get_db)])
def get_feed_posts(current_user: UserModel = Depends(get_current_user)):
    return post_ops.get_feed_posts(current_user)


@router.post("/upload-image", status_code=200, dependencies=[Depends(get_db)])
async def upload_image(
    image: UploadFile = File(...),
    is_profile: bool = Body(False),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        with db.atomic():
            image_model = ImageModel.create(
                user_id=current_user.id,
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
        return str(image_model.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"msg": repr(e)})


@router.get("/get-image", status_code=200, dependencies=[Depends(get_db)])
async def get_image(image_id, is_profile: bool = False):
    return post_ops.get_image(image_id, is_profile)


@router.delete("/delete-image", status_code=200, dependencies=[Depends(get_db)])
async def delete_image(
    image_id: UUID, current_user: UserModel = Depends(get_current_user)
):
    if not check_user_access(current_user.id, image_id, "image"):
        detail = {
            "user_id": str(current_user.id),
            "post_id": str(image_id),
            "msg": "Access denied.",  # noqa: E501
        }
        raise HTTPException(status_code=403, detail=detail)
    return post_ops.delete_image(image_id)


@router.delete("/delete-post", status_code=200, dependencies=[Depends(get_db)])
async def delete_post(
    post_id: UUID, current_user: UserModel = Depends(get_current_user)
):
    if not check_user_access(current_user.id, post_id, "post"):
        detail = {
            "user_id": str(current_user.id),
            "post_id": str(post_id),
            "msg": "Access denied.",  # noqa: E501
        }
        raise HTTPException(status_code=403, detail=detail)
    post_ops.delete_post(post_id)
