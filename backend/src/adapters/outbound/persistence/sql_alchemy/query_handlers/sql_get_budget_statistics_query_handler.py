from application.dtos import CategoryStatisticsRecordDTO, MoneyDTO, StatisticsRecordDTO

# from application.exceptions import NotFoundError # Removed incorrect import
from application.queries import GetBudgetStatisticsQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import StatisticsRecordNotFoundError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import StatisticsRecordModel


class SQLGetBudgetStatisticsQueryHandler(
    QueryHandler[GetBudgetStatisticsQuery, StatisticsRecordDTO]
):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def handle(self, query: GetBudgetStatisticsQuery) -> StatisticsRecordDTO:
        # Find the latest statistics record for the given budget and user
        stmt = (
            select(StatisticsRecordModel)
            .where(StatisticsRecordModel.budget_id == query.budget_id)
            .where(StatisticsRecordModel.user_id == query.user_id)  # Add user_id check
            .options(selectinload(StatisticsRecordModel.category_statistics))
            .order_by(StatisticsRecordModel.creation_date.desc())
            .limit(1)
        )

        result = await self._session.scalar(stmt)

        # Check if statistics exist and belong to the user
        if not result or result.user_id != query.user_id:
            raise StatisticsRecordNotFoundError(
                f"Statistics not found for budget id {query.budget_id}. "
                f"Statistics might not have been generated yet or do not belong to the user."
            )

        # Removed date conversion as model now uses datetime
        # creation_datetime = datetime.combine(result.creation_date, time.min)

        return StatisticsRecordDTO(
            id=result.id,
            user_id=result.user_id,
            budget_id=result.budget_id,
            current_balance=MoneyDTO(
                amount=result.current_balance.amount,
                currency=result.current_balance.currency,
            ),
            daily_available_amount=MoneyDTO(
                amount=result.daily_available_amount.amount,
                currency=result.daily_available_amount.currency,
            ),
            daily_average=MoneyDTO(
                amount=result.daily_average.amount,
                currency=result.daily_average.currency,
            ),
            used_limit=MoneyDTO(
                amount=result.used_limit.amount,
                currency=result.used_limit.currency,
            ),
            creation_date=result.creation_date,  # Use datetime directly from model
            categories_statistics=[  # Map category statistics
                CategoryStatisticsRecordDTO(
                    id=cat_stat.id,
                    category_id=cat_stat.category_id,
                    current_balance=MoneyDTO(
                        amount=cat_stat.current_balance.amount,
                        currency=cat_stat.current_balance.currency,
                    ),
                    daily_available_amount=MoneyDTO(
                        amount=cat_stat.daily_available_amount.amount,
                        currency=cat_stat.daily_available_amount.currency,
                    ),
                    daily_average=MoneyDTO(
                        amount=cat_stat.daily_average.amount,
                        currency=cat_stat.daily_average.currency,
                    ),
                    used_limit=MoneyDTO(
                        amount=cat_stat.used_limit.amount,
                        currency=cat_stat.used_limit.currency,
                    ),
                )
                for cat_stat in result.category_statistics
            ],
        )
