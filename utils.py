# type: ignore
"""Primary API."""
from typing import Any
from uuid import UUID

from database.database import db
from database.models import UserModel, PostModel, FollowerModel, ImageModel

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
TIME_ALLOWED_CHANGE_MESSAGE_HOURS = 48
VISIBILITY_TYPES = ["public", "friends", "personal"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserAuth(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    description: Optional[str] = None
    disabled: Optional[bool] = None


model_translator = {
    "user": UserModel,
    "post": PostModel,
    "follower": FollowerModel,
    "image": ImageModel,
}


# def get_user_info(user_email):
#     user = UserModel.get_or_none(UserModel.email == user_email)
#     if user is None:
#         detail = {"msg": f"User Does not Exist: {user_email}"}
#         raise HTTPException(status_code=404, detail=detail)
#
#     user_info = {
#         "id": user.id,
#         "email": user.email,
#         "username": user.username,
#         "first_name": user.first_name,
#         "last_name": user.last_name,
#         "full_name": f"{user.first_name} {user.last_name}",
#         "create_time": user.create_time,
#         "password_hash": user.password_hash,
#         "disabled": user.disabled
#     }
#     user_info.update(get_followers_info(user.id))
#     return user_info


def query_fetchall(query: Any) -> Any:
    """Perform fetchall on peewee query."""
    cursor = db.execute(query)
    return cursor.fetchall()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(email, password: str):
    user = UserModel.get_or_none(UserModel.email == email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_auth(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    # token_data.username will be an email/username. Will handle this in frontend!
    user = UserModel.get_or_none(UserModel.email == token_data.username)
    if user is None:
        raise credentials_exception
    return user


def common_user_auth(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        if not UserModel.get_or_none(UserModel.email == username):
            detail = {"msg": f"User Does not Exist: {username}"}
            raise HTTPException(status_code=404, detail=detail)
    except JWTError:
        raise credentials_exception


# def get_current_active_user(current_user: dict = Depends(get_current_user_auth)):
#     if current_user.get("disabled"):
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


def get_current_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    current_user = UserModel.get_or_none(UserModel.username == username)
    return current_user


def _get_object_user_id(object_model, object_type):
    if object_type in ["user", "post", "follower", "image"]:
        return object_model.user_id.id
    # Not needed for now
    elif object_type == "room":
        return object_model.owner_id.id


def check_user_access(user_id: UUID, object_id: UUID, object_type: str):
    user = UserModel.get_or_none(UserModel.id == user_id)
    if user is None:
        detail = {"msg": f"User Does not Exist: {user_id}"}
        raise HTTPException(status_code=404, detail=detail)

    model = model_translator.get(object_type)
    if model is None:
        detail = {"msg": f"Object Type Does not Exist: {object_type}"}
        raise HTTPException(status_code=404, detail=detail)

    object_model = model.get_or_none(model.id == object_id)
    if object_model is None:
        detail = {"msg": f"Object Does not Exist: {object_id}"}
        raise HTTPException(status_code=404, detail=detail)

    object_user_id = _get_object_user_id(object_model, object_type)
    return object_user_id == user_id


def login_user(user: UserAuth, Authorize: AuthJWT):
    """
    With authjwt_cookie_csrf_protect set to True, set_access_cookies() and
    set_refresh_cookies() will now also set the non-httponly CSRF cookies
    """
    user = authenticate_user(user.username, user.password)
    if not user:
        raise HTTPException(status_code=401, detail="Bad username or password")

    # Create the tokens and passing to set_access_cookies or set_refresh_cookies
    access_token = Authorize.create_access_token(subject=user.username)
    refresh_token = Authorize.create_refresh_token(subject=user.username)

    # Set the JWT and CSRF double submit cookies in the response
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return {"msg": "Successfully login"}


def refresh_token(Authorize: AuthJWT):
    Authorize.jwt_refresh_token_required()
    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    # Set the JWT and CSRF double submit cookies in the response
    Authorize.set_access_cookies(new_access_token)


def get_user(user_email):
    user = UserModel.get_or_none(UserModel.email == user_email)
    if user is None:
        msg = f"User Does not Exist: {user_email}"
        raise HTTPException(status_code=404, detail={"msg": msg})
    return user


def get_user_by_id(user_id):
    user = UserModel.get_or_none(UserModel.id == user_id)
    if user is None:
        msg = f"User Does not Exist: {user_id}"
        raise HTTPException(status_code=404, detail={"msg": msg})
    return user
