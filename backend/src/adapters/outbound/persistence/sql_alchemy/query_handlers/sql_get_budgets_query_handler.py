from datetime import datetime

from application.dtos import (
    BudgetDTO,
    BudgetStrategyDTO,
    CategoryDTO,
    MoneyDTO,
    PaginatedItemDTO,
)
from application.queries import GetBudgetsQuery
from application.queries.handlers import QueryHandler
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import BudgetModel


class SQLGetBudgetsQueryHandler(
    QueryHandler[GetBudgetsQuery, PaginatedItemDTO[BudgetDTO]]
):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def handle(self, query: GetBudgetsQuery) -> PaginatedItemDTO[BudgetDTO]:
        # Calculate offset
        skip = (query.page - 1) * query.limit

        # Base query
        stmt = (
            select(BudgetModel)
            .where(BudgetModel.user_id == query.user_id)
            .options(selectinload(BudgetModel.categories))  # Eager load categories
            .offset(skip)
            .limit(query.limit)
        )

        # Total count query - using standard syntax
        count_stmt = select(func.count(BudgetModel.id)).where(
            BudgetModel.user_id == query.user_id
        )
        # Apply status filter correctly to count query
        if query.status:
            now = datetime.now()
            if query.status.lower() == "active":
                active_filter = (
                    BudgetModel.start_date <= now,
                    BudgetModel.end_date >= now,
                    (
                        BudgetModel.deactivation_date.is_(None)
                        | (BudgetModel.deactivation_date > now)
                    ),
                )
                stmt = stmt.where(*active_filter)
                count_stmt = count_stmt.where(*active_filter)
            elif query.status.lower() == "expired":
                expired_filter = (BudgetModel.end_date < now) | (
                    BudgetModel.deactivation_date <= now
                )
                stmt = stmt.where(expired_filter)
                count_stmt = count_stmt.where(expired_filter)

        # Apply sorting
        if query.sort:
            sort_column = getattr(BudgetModel, query.sort, None)
            if sort_column:
                stmt = stmt.order_by(sort_column)
        else:
            # Default sort
            stmt = stmt.order_by(BudgetModel.created_at.desc())

        # Execute queries
        result = await self._session.scalars(stmt)
        total_count = await self._session.scalar(count_stmt) or 0

        # Map to DTOs
        budget_dtos = [
            BudgetDTO(
                id=budget.id,
                user_id=budget.user_id,
                name=budget.name,
                total_limit=MoneyDTO(
                    amount=budget.total_limit.value.amount,
                    currency=budget.total_limit.value.currency,
                ),
                currency=budget.total_limit.value.currency,
                start_date=budget.start_date,
                end_date=budget.end_date,
                strategy=BudgetStrategyDTO(
                    type=budget.strategy.strategy_input.strategy_type.value,
                ),
                deactivation_date=budget.deactivation_date,
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
                    for cat in budget.categories
                ],
            )
            for budget in result.all()
        ]

        return PaginatedItemDTO(
            items=budget_dtos, total=total_count, skip=skip, limit=query.limit
        )
