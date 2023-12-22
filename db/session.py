from settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import registry
from sqlalchemy import MetaData


metadata = MetaData()
engine = create_engine(settings.database.url)
mapper_registry = registry()


get_session = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)
