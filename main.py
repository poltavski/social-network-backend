# type: ignore
"""Primary API."""
# import logging
import uvicorn

import routers.users.router as user_router
import routers.followers.router as follower_router
import routers.posts.router as post_router

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from utils import (
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    get_current_active_user,
    User,
    Token,
)

# logger = logging.Logger()

app = FastAPI(default_response_class=ORJSONResponse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = FastAPI()


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: dict = Depends(get_current_active_user)):
    # TODO: user information for posts and stuff. May be deleted if not used.
    return [{"item_id": "Foo", "owner": current_user.get("username")}]


@app.get("/debug/hash_password/")
async def hash_password(password: str):
    return get_password_hash(password)


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
    return "Hello from social network web app."


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
