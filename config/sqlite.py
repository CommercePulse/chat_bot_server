from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import declarative_base
from models import schemas

engine = create_engine('sqlite:///bot_namespace.db')


def init_db():
    Base = declarative_base()
    Base.metadata.create_all(engine,checkfirst=True)
    # schemas.Base.metadata.create_all(engine, checkfirst=True)


 