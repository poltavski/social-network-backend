from database.database import db
from typing import Any


def query_fetchall(query: Any) -> Any:
    """Perform fetchall on peewee query."""
    cursor = db.execute(query)
    return cursor.fetchall()
