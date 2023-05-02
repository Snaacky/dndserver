import arrow
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Boolean, Enum, Integer, String, Text
from sqlalchemy_utils import ArrowType

from dndserver.config import config
from dndserver.database import db
from dndserver.enums import CharacterClass, Gender


base = declarative_base()


class Account(base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    username = Column(String(20), unique=True, nullable=False)
    password = Column(Text)
    secret_token = Column(String(21))
    created_at = Column(ArrowType, default=arrow.utcnow())
    ban_type = Column(Integer)

    def save(self):
        db.add(self)
        db.commit()


class Character(base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    account_id = Column(Integer)
    nickname = Column(String(20), unique=True)
    gender = Column(Enum(Gender))
    character_class = Column(Enum(CharacterClass))
    created_at = Column(ArrowType, default=arrow.utcnow())
    level = Column(Integer, default=config.game.settings.starting_level)
    experience = Column(Integer, default=0)
    karma_rating = Column(Integer, default=0)
    streaming_nickname = Column(String(15))

    perk0 = Column(String, default="")
    perk1 = Column(String, default="")
    perk2 = Column(String, default="")
    perk3 = Column(String, default="")

    skill0 = Column(String, default="")
    skill1 = Column(String, default="")

    spell0 = Column(String, default="")
    spell1 = Column(String, default="")
    spell2 = Column(String, default="")
    spell3 = Column(String, default="")
    spell4 = Column(String, default="")
    spell5 = Column(String, default="")
    spell6 = Column(String, default="")
    spell7 = Column(String, default="")
    spell8 = Column(String, default="")
    spell9 = Column(String, default="")

    ranking_coin = Column(Integer, default=0)
    ranking_kill = Column(Integer, default=0)
    ranking_escape = Column(Integer, default=0)
    ranking_adventure = Column(Integer, default=0)
    ranking_lich = Column(Integer, default=0)
    ranking_ghostking = Column(Integer, default=0)

    def save(self):
        db.add(self)
        db.commit()

    def delete(self):
        db.delete(self)
        db.commit()


class Item(base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    character_id = Column(Integer)
    item_id = Column(String)
    quantity = Column(Integer)
    inventory_id = Column(Integer)
    slot_id = Column(Integer)

    ammo_count = Column(Integer, default=0)

    def save(self):
        db.add(self)
        db.commit()

    def delete(self):
        db.delete(self)
        db.commit()


class ItemAttribute(base):
    __tablename__ = "item_attributes"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    item_id = Column(Integer)
    primary = Column(Boolean)
    property = Column(String)
    value = Column(Integer)

    def save(self):
        db.add(self)
        db.commit()

    def delete(self):
        db.delete(self)
        db.commit()


class Hwid(base):
    __tablename__ = "hwids"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    account_id = Column(Integer)
    hwid = Column(String(64), unique=True)
    is_banned = Column(Boolean)
    seen_at = Column(ArrowType, default=arrow.utcnow())

    def save(self):
        db.add(self)
        db.commit()

    def delete(self):
        db.delete(self)
        db.commit()


class BlockedUser(base):
    __tablename__ = "blocked_users"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    blocked_by = Column(Integer)  # Character ID
    account_id = Column(Integer)
    character_id = Column(Integer)
    nickname = Column(String(20))
    gender = Column(Enum(Gender))
    character_class = Column(Enum(CharacterClass))
    blocked_at = Column(ArrowType, default=arrow.utcnow())

    def save(self):
        db.add(self)
        db.commit()

    def delete(self):
        db.delete(self)
        db.commit()


# characters: store all logins in a database and grab the latest from that
# class Login(base):
#     __tablename__ = "logins"
#     id = Column(Integer, primary_key=True, autoincrement="auto")
