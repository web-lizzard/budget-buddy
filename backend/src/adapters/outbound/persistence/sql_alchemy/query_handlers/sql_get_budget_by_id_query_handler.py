from application.dtos import BudgetDTO, BudgetStrategyDTO, CategoryDTO, MoneyDTO
from application.queries import GetBudgetByIdQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import BudgetNotFoundError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import BudgetModel


class SQLGetBudgetByIdQueryHandler(QueryHandler[GetBudgetByIdQuery, BudgetDTO]):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def handle(self, query: GetBudgetByIdQuery) -> BudgetDTO:
        stmt = (
            select(BudgetModel)
            .where(BudgetModel.id == query.budget_id)
            .options(selectinload(BudgetModel.categories))
        )

        result = await self._session.scalar(stmt)

        if not result or result.user_id != query.user_id:
            raise BudgetNotFoundError(f"Budget with id {query.budget_id} not found.")

        return BudgetDTO(
            id=result.id,
            user_id=result.user_id,
            name=result.name,
            total_limit=MoneyDTO(
                amount=result.total_limit.value.amount,
                currency=result.total_limit.value.currency,
            ),
            currency=result.total_limit.value.currency,
            start_date=result.start_date,
            end_date=result.end_date,
            strategy=BudgetStrategyDTO(
                type=result.strategy.strategy_input.strategy_type.value,
            ),
            deactivation_date=result.deactivation_date,
            categories=[  # Map categories
                CategoryDTO(
                    id=cat.id,
                    name=cat.name,
                    limit=MoneyDTO(
                        amount=cat.limit.value.amount,
                        currency=cat.limit.value.currency,
                    ),
                    budget_id=cat.budget_id,
                )
                for cat in result.categories
            ],
        )
