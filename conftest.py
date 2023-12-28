import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from common.db.session import metadata
from common.db.registry import start_mappers
from sqlalchemy.pool import StaticPool


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def in_memory_db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    metadata.create_all(engine)

    return engine


@pytest.fixture
def session(in_memory_db):
    clear_mappers()
    start_mappers()
    db = sessionmaker(bind=in_memory_db)()
    try:
        yield db
    finally:
        db.close()


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
