from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings import settings

engine = create_engine(url=settings.database.url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
