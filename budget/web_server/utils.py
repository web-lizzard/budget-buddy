from fastapi import Depends
from typing import Annotated
from common.db import session, repository
from sqlalchemy.orm import Session
from budget.domain import model


def get_category_repository(
    session: Annotated[Session, session.get_database]
) -> repository.Repository:
    return repository.SQLRepository(model=model.Budget, session=session)


def get_budget_repository(
    session: Annotated[Session, session.get_database]
) -> repository.Repository:
    return repository.SQLRepository(model=model.Budget, session=session)
