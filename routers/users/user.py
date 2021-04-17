from fastapi import (
    APIRouter,
    Depends,
    Header,
)
from uuid import UUID
from database.models import UserModel
from database.database import db
from uuid import uuid4
import time
router = APIRouter()


@router.get("", status_code=200)
def get_project_alerts():
    """Hello World."""
    return "Hello, World"


@router.post("/create-user", status_code=200)
def create_user():
    with db.atomic():
        user = UserModel.create(
            id=uuid4(),
            email='random@gmail.com',
            first_name='randomUser',
            last_name='randomUserLastName',
            password_hash='nu tut ya hz konechno',
            create_time=int(time.time()),
            username='RandomUserUsername'
        )

    return {"proj_uuid": str(user.id)}
