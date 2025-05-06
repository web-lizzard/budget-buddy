from datetime import datetime
from uuid import UUID

from application.dtos import CategoryStatisticsRecordDTO, MoneyDTO, StatisticsRecordDTO
from application.queries import GetBudgetStatisticsQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import StatisticsRecordNotFoundError
from domain.ports.clock import Clock
from domain.value_objects.money import Money
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import BudgetModel, CategoryModel, StatisticsRecordModel


class SQLGetBudgetStatisticsQueryHandler(
    QueryHandler[GetBudgetStatisticsQuery, StatisticsRecordDTO]
):
    def __init__(self, session: AsyncSession, clock: Clock):
        self._session = session
        self._clock = clock

    async def handle(self, query: GetBudgetStatisticsQuery) -> StatisticsRecordDTO:
        stmt = (
            select(StatisticsRecordModel)
            .where(StatisticsRecordModel.budget_id == query.budget_id)
            .where(StatisticsRecordModel.user_id == query.user_id)
            .options(selectinload(StatisticsRecordModel.category_statistics))
            .order_by(StatisticsRecordModel.creation_date.desc())
            .limit(1)
        )

        result = await self._session.scalar(stmt)

        if not result or result.user_id != query.user_id:
            raise StatisticsRecordNotFoundError(
                f"Statistics not found for budget id {query.budget_id}. "
                f"Statistics might not have been generated yet or do not belong to the user."
            )

        budget_stmt = (
            select(BudgetModel)
            .where(BudgetModel.id == query.budget_id)
            .options(selectinload(BudgetModel.categories))
        )
        budget_model = await self._session.scalar(budget_stmt)

        if not budget_model or budget_model.user_id != query.user_id:
            raise StatisticsRecordNotFoundError(
                f"Budget with id {query.budget_id} not found. "
                f"Cannot recalculate daily available amount."
            )

        today = self._clock.now()

        days_remaining = self._calculate_days_remaining(budget_model.end_date, today)

        overall_daily_available = self._calculate_daily_available(
            budget_model.total_limit.value, result.current_balance, days_remaining
        )

        categories_statistics = []
        for cat_stat in result.category_statistics:
            category = self._get_category_by(cat_stat.category_id, budget_model)
            if category:
                cat_daily_available = self._calculate_daily_available(
                    category.limit.value, cat_stat.current_balance, days_remaining
                )

                categories_statistics.append(
                    CategoryStatisticsRecordDTO(
                        id=cat_stat.id,
                        category_id=cat_stat.category_id,
                        current_balance=MoneyDTO(
                            amount=cat_stat.current_balance.to_float(),
                            currency=cat_stat.current_balance.currency,
                        ),
                        daily_available_amount=MoneyDTO(
                            amount=cat_daily_available.to_float(),
                            currency=cat_daily_available.currency,
                        ),
                        daily_average=MoneyDTO(
                            amount=cat_stat.daily_average.to_float(),
                            currency=cat_stat.daily_average.currency,
                        ),
                        used_limit=MoneyDTO(
                            amount=cat_stat.used_limit.to_float(),
                            currency=cat_stat.used_limit.currency,
                        ),
                    )
                )

        return StatisticsRecordDTO(
            id=result.id,
            user_id=result.user_id,
            budget_id=result.budget_id,
            current_balance=MoneyDTO(
                amount=result.current_balance.to_float(),
                currency=result.current_balance.currency,
            ),
            daily_available_amount=MoneyDTO(
                amount=overall_daily_available.to_float(),
                currency=overall_daily_available.currency,
            ),
            daily_average=MoneyDTO(
                amount=result.daily_average.to_float(),
                currency=result.daily_average.currency,
            ),
            used_limit=MoneyDTO(
                amount=result.used_limit.to_float(),
                currency=result.used_limit.currency,
            ),
            creation_date=result.creation_date,
            categories_statistics=categories_statistics,
        )

    def _calculate_days_remaining(self, end_date_dt: datetime, today: datetime) -> int:
        """Calculates remaining calendar days using datetime, minimum 1."""
        delta = end_date_dt - today
        if delta.total_seconds() < 0:
            return 1
        return delta.days + 1

    def _safe_divide_money(self, money, days: int):
        """Divides Money amount (smallest units) by days."""
        from decimal import ROUND_HALF_UP, Decimal

        if days <= 0:
            return type(money)(0, money.currency)
        try:
            daily_amount_decimal = (Decimal(money.amount) / Decimal(days)).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
            daily_amount_int = int(daily_amount_decimal)
            return type(money)(daily_amount_int, money.currency)
        except Exception:
            return type(money)(0, money.currency)

    def _calculate_daily_available(
        self, limit: Money, current_balance: Money, days_remaining: int
    ):
        """Calculates daily available amount based on current balance and days remaining."""
        # Ensure currencies match
        if limit.currency != current_balance.currency:
            return type(limit)(0, limit.currency)

        total_available = limit.add(current_balance)
        if total_available.amount < 0:
            # No budget available
            return type(limit)(0, limit.currency)

        return self._safe_divide_money(total_available, days_remaining)

    def _get_category_by(
        self, category_id: UUID, budget_model: BudgetModel
    ) -> CategoryModel | None:
        budget_categories = budget_model.categories
        for category in budget_categories:
            if category.id == category_id:
                return category
        return None
