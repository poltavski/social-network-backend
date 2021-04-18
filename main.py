# type: ignore
"""Primary API."""
# import logging
import uvicorn
# from .extra import psycopg2_register_uuid_stub  # noqa: F401, I201, I100
import routers.users.router as user_router
import routers.followers.router as follower_router
import routers.posts.router as post_router

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

# logger = logging.Logger()
# Use ORJSON decoder for parsing responses from postgresql
# Global service logger

app = FastAPI(default_response_class=ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    user_router.router,
    prefix="/user",
    tags=["user"],
    # dependencies=[Depends(get_db)],
)

app.include_router(
    follower_router.router,
    prefix="/follower",
    tags=["follower"],
    # dependencies=[Depends(get_db)],
)

app.include_router(
    post_router.router,
    prefix="/post",
    tags=["post"],
    # dependencies=[Depends(get_db)],
)


@app.middleware("http")
async def run_middleware(request: Request, call_next):
    """Middleware that runs before a request is processed and a response is returned.

    The exit logic of dependencies with yield runs after the middleware. Background
    tasks run after the middleware.
    """
    response = await call_next(request)
    # Delete the context logger if it exists
    # logger.delete()
    return response


@app.get("/")
def index():
    """Index route."""
    return "Hello from NE Yogi API."


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")