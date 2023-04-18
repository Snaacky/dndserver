import dataset
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from dndserver.config import config

url = f"sqlite:///{config.database.file}"


def get():
    return dataset.connect(url)


def setup():
    engine = create_engine(url)
    if not database_exists(engine.url):
        create_database(engine.url)

    db = get()
    if "users" not in db:
        users = db.create_table("users")
        users.create_column("username", db.types.text)  # 2 characters, 20 characters
        users.create_column("password", db.types.text)
        users.create_column("hwids", db.types.text)
        users.create_column("build_version", db.types.text)
        users.create_column("is_banned", db.types.integer)  # 12 = ban user, 13 = ban cheater, 14 = ban inappropriate name, 15 = ban etc, 16 = hwid ban
