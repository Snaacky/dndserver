import time

import dataset
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from dndserver.config import config

url = f"sqlite:///{config.database.file}"


def get():
    """Return an opened connection to the database."""
    return dataset.connect(url)


def setup():
    """Temporary initialization function to make sure the database is setup properly."""
    engine = create_engine(url)
    if not database_exists(engine.url):
        create_database(engine.url)

    db = get()

    if "users" not in db:
        users = db.create_table("users")
        users.create_column("username", db.types.text)  # 2 characters min, 20 characters max
        users.create_column("password", db.types.text)
        users.create_column("hwids", db.types.text)
        users.create_column("build_version", db.types.text)
        users.create_column("is_banned", db.types.integer, default=None)  # 12 = ban user, 13 = ban cheater, 14 = ban inappropriate name, 15 = ban etc, 16 = hwid ban
        users.create_column("secret_token", db.types.text, default=None)

    if "characters" not in db:
        chars = db.create_table("characters")
        chars.create_column("owner_id", db.types.integer)
        chars.create_column("nickname", db.types.text)  # ?? characters min, 20 characters max
        chars.create_column("gender", db.types.integer)
        chars.create_column("character_class", db.types.text)
        chars.create_column("created_at", db.types.integer, default=int(time.time()))
        chars.create_column("level", db.types.integer, default=1)
        chars.create_column("last_logged_at", db.types.integer, default=int(time.time()))

    db.commit()
    db.close()
