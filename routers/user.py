from fastapi import (
    APIRouter,
    Depends,
    Header,
)
from uuid import UUID

router = APIRouter()

@router.get("", status_code=200)
def get_project_alerts(
    proj_uuid: UUID = None,
    token: str = Header(None, alias="Authorization"),
):
    """Hello World."""
    return "Hello, World"