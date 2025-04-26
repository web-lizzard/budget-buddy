import uuid
from typing import Tuple

from domain.aggregates.budget import Budget
from domain.exceptions import BudgetNotFoundError, NotCompatibleVersionError
from domain.ports.budget_repository import BudgetRepository
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..mappers.budget_mapper import (
    map_budget_domain_to_model,
    map_budget_model_to_domain,
)
from ..models import BudgetModel


class SQLAlchemyBudgetRepository(BudgetRepository):
    """SQLAlchemy implementation of the BudgetRepository port."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by(
        self, budget_id: uuid.UUID, user_id: uuid.UUID
    ) -> Tuple[int, Budget]:
        """Find budget by id and user id, eagerly loading categories."""
        stmt = (
            select(BudgetModel)
            .where(BudgetModel.id == budget_id, BudgetModel.user_id == user_id)
            .options(selectinload(BudgetModel.categories))
        )
        result = await self._session.execute(stmt)
        try:
            budget_model = result.scalars().one()
            return budget_model.version, map_budget_model_to_domain(budget_model)
        except NoResultFound:
            raise BudgetNotFoundError(str(budget_id))

    async def save(self, budget: Budget, version: int) -> None:
        """Save budget to repository, checking for version conflicts."""
        existing_model = await self._session.get(
            BudgetModel, budget.id, options=[selectinload(BudgetModel.categories)]
        )

        if existing_model:
            if existing_model.version != version:
                raise NotCompatibleVersionError(
                    str(budget.id),
                    expected_version=version,
                    actual_version=existing_model.version,
                )
            budget_model = map_budget_domain_to_model(budget, existing_model)
            budget_model.version = version + 1
            await self._session.merge(budget_model)
        else:
            if version != 0:
                raise NotCompatibleVersionError(
                    f"Budget with ID {budget.id} not found, but expected version was {version}. Cannot create.",
                    expected_version=version,
                    actual_version=0,
                )

            budget_model = map_budget_domain_to_model(budget)

            budget_model.version = 1
            self._session.add(budget_model)
