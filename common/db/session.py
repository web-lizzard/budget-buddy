from settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import registry
from sqlalchemy import MetaData


metadata = MetaData()
mapper_registry = registry()
engine = create_engine(settings.database.url)


get_session = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def get_database():
    db = get_session()
    try:
        yield db
    finally:
        db.close()
