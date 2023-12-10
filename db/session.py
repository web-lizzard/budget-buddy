from settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .model import metadata

engine = create_engine(settings.database.url)
metadata.create_all(engine)

get_session = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)
