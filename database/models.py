# type: ignore
"""These are the data models used for queries via the peewee ORM."""
import uuid

from peewee import BooleanField
from peewee import ForeignKeyField
from peewee import Model
from peewee import CharField
from peewee import TimestampField
from peewee import UUIDField
from peewee import CompositeKey
from peewee import TextField
from playhouse.postgres_ext import ArrayField

import database.settings as settings
from .database import db


class UserModel(Model):
    """Model for users."""

    class Meta:
        """TODO document this."""

        database = db
        table_name = settings.USERS_TABLE

    id = UUIDField(unique=True, null=False, primary_key=True, default=uuid.uuid4)
    username = CharField(unique=True, null=False)
    email = CharField(unique=True, null=False)
    first_name = CharField(null=False)
    last_name = CharField(null=False)
    description = CharField(null=True)
    password_hash = CharField(null=False)
    create_time = TimestampField(null=True, default=None, resolution=0, utc=False)
    disabled = BooleanField(null=False, default=True)


class FollowerModel(Model):
    """Model for followers."""

    class Meta:
        """TODO document this."""

        database = db
        table_name = settings.FOLLOWERS_TABLE
        primary_key = CompositeKey("user_id", "follower_id")

    user_id = ForeignKeyField(
        UserModel,
        on_delete="CASCADE",
        on_update="CASCADE",
        column_name="user_id",
    )
    follower_id = ForeignKeyField(
        UserModel,
        on_delete="CASCADE",
        on_update="CASCADE",
        column_name="follower_id",
    )
    create_time = TimestampField(default=None, resolution=0, utc=False)


class ImageModel(Model):
    """Model for images."""

    class Meta:
        """TODO document this."""

        database = db
        table_name = settings.IMAGES_TABLE

    id = UUIDField(unique=True, null=False, primary_key=True, default=uuid.uuid4)
    user_id = ForeignKeyField(
        UserModel,
        on_delete="CASCADE",
        on_update="CASCADE",
        column_name="user_id",
    )
    format = CharField(null=True)
    is_profile = BooleanField(default=False)
    create_time = TimestampField(default=None, resolution=0, utc=False)


class PostModel(Model):
    """Model for posts."""

    class Meta:
        """TODO document this."""

        database = db
        table_name = settings.POSTS_TABLE

    id = UUIDField(unique=True, null=False, primary_key=True, default=uuid.uuid4)
    user_id = ForeignKeyField(
        UserModel,
        on_delete="CASCADE",
        on_update="CASCADE",
        column_name="user_id",
    )
    image_id = ForeignKeyField(
        ImageModel,
        on_delete="CASCADE",
        on_update="CASCADE",
        column_name="image_id",
        null=True,
    )
    content = CharField(null=True)
    create_time = TimestampField(default=None, resolution=0, utc=False)
    edited = BooleanField(null=False, default=False)
    edit_time = TimestampField(default=None, resolution=0, utc=False)
    visibility = CharField(null=False, default="public")
    likes = ArrayField(null=True, field_class=TextField)
