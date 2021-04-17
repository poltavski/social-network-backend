# type: ignore
"""These are the data models used for queries via the peewee ORM."""
from peewee import BigAutoField
from peewee import BigIntegerField
from peewee import BooleanField
from peewee import DoubleField
from peewee import FloatField
from peewee import ForeignKeyField
from peewee import IntegerField
from peewee import ManyToManyField
from peewee import Model
from peewee import SmallIntegerField
from peewee import CharField
from peewee import TextField
from peewee import TimestampField
from peewee import UUIDField
from peewee import fn
from playhouse.postgres_ext import ArrayField
from playhouse.postgres_ext import BinaryJSONField
from playhouse.postgres_ext import TSVectorField

import database.settings as settings
from .database import db


class UserModel(Model):
    """Model for users."""

    class Meta:
        """TODO document this."""

        database = db
        table_name = settings.USERS_TABLE
    id = UUIDField(unique=True, null=False)
    username = CharField(unique=True, null=False)
    email = CharField(unique=True, null=False)
    first_name = CharField(null=False)
    last_name = CharField(null=False)
    description = CharField(null=True)
    password_hash = CharField(null=False)
    create_time = TimestampField(null=True, default=None, resolution=0, utc=False)


class FollowerModel(Model):
    """Model for users."""

    class Meta:
        """TODO document this."""

        database = db
        table_name = settings.FOLLOWERS_TABLE

    user_id = ForeignKeyField(
        UserModel,
        on_delete="CASCADE",
        on_update="CASCADE",
        column_name="id",
    )
    follower_id = ForeignKeyField(
        UserModel,
        on_delete="CASCADE",
        on_update="CASCADE",
        column_name="id",
    )
    create_time = TimestampField(default=None, resolution=0, utc=False)


class ImageModel(Model):
    """Model for images."""

    class Meta:
        """TODO document this."""

        database = db
        table_name = settings.IMAGES_TABLE
    id = UUIDField(unique=True)
    user_id = ForeignKeyField(
        UserModel,
        on_delete="CASCADE",
        on_update="CASCADE",
        column_name="id",
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

    id = UUIDField(unique=True)
    user_id = ForeignKeyField(
        UserModel,
        on_delete="CASCADE",
        on_update="CASCADE",
        column_name="id",
    )
    image_id = ForeignKeyField(
        ImageModel,
        on_delete="CASCADE",
        on_update="CASCADE",
        column_name="id",
    )
    content = CharField(null=True)
    create_time = TimestampField(default=None, resolution=0, utc=False)


class RoomUserModel(Model):
    """Model for posts."""

    class Meta:
        """TODO document this."""

        database = db
        table_name = settings.POSTS_TABLE
