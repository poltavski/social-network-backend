from os import environ

from boto3.session import Session


env = environ.get("ENV")

# Database settings. Limited by user's/service's IAM permissions to access these.

DATABASE = {
        "db_name": environ["DB_NAME"],
        "user": environ["DB_USER"],
        "password": environ["DB_PASSWORD"],
        "host": environ["DB_HOST"],
        "port": environ["DB_PORT"],
        "autorollback": True,
}

# Tables
FOLLOWERS_TABLE = "followers"
IMAGES_TABLE = "images"
POSTS_TABLE = "posts"
ROOM_USERS_TABLE = "room_users"
ROOMS_TABLE = "rooms"
USERS_TABLE = "users"
