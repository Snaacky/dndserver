from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite:///dndserver.db")
session = sessionmaker(bind=engine)
db = session()
