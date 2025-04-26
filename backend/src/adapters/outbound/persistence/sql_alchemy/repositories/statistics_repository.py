import uuid
from datetime import date, datetime

from domain.aggregates.statistics_record import StatisticsRecord
from domain.exceptions.statistics_not_found_exceptions import StatisticsNotFoundError
from domain.ports.outbound.statistics_repository import StatisticsRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..mappers.statistics_mapper import (
    map_statistics_record_domain_to_model,
    map_statistics_record_model_to_domain,
)
from ..models import CategoryStatisticsRecordModel, StatisticsRecordModel


class SQLAlchemyStatisticsRepository(StatisticsRepository):
    """SQLAlchemy implementation of the StatisticsRepository port."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, statistics_record: StatisticsRecord) -> None:
        """Saves (creates or updates) a statistics record using merge."""
        record_model = map_statistics_record_domain_to_model(statistics_record)
        await self._session.merge(record_model)

    async def find_by_id(
        self, statistic_id: uuid.UUID, user_id: uuid.UUID
    ) -> StatisticsRecord:
        """Finds a statistics record by its ID for a specific user."""
        stmt = (
            select(StatisticsRecordModel)
            .where(
                StatisticsRecordModel.id == statistic_id,
                StatisticsRecordModel.user_id == user_id,
            )
            .options(selectinload(StatisticsRecordModel.category_statistics))
        )
        result = await self._session.execute(stmt)
        record_model = result.scalars().one_or_none()

        if record_model is None:
            raise StatisticsNotFoundError(
                f"Statistics record with ID {statistic_id} not found for user {user_id}"
            )
        return map_statistics_record_model_to_domain(record_model)

    async def find_by_budget_id(
        self, budget_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds all statistics records for a specific budget and user."""
        stmt = (
            select(StatisticsRecordModel)
            .where(
                StatisticsRecordModel.budget_id == budget_id,
                StatisticsRecordModel.user_id == user_id,
            )
            .options(selectinload(StatisticsRecordModel.category_statistics))
            .order_by(StatisticsRecordModel.creation_date.desc())
        )
        result = await self._session.execute(stmt)
        record_models = result.scalars().all()
        return [map_statistics_record_model_to_domain(model) for model in record_models]

    async def find_by_category_id(
        self, category_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds all statistics records containing a specific category_id for a user."""
        stmt = (
            select(StatisticsRecordModel)
            .join(StatisticsRecordModel.category_statistics)
            .where(
                StatisticsRecordModel.user_id == user_id,
                CategoryStatisticsRecordModel.category_id == category_id,
            )
            .options(selectinload(StatisticsRecordModel.category_statistics))
            .distinct()
            .order_by(
                StatisticsRecordModel.creation_date.desc()
            )  # Optional: order by date
        )
        result = await self._session.execute(stmt)
        record_models = result.scalars().all()
        return [map_statistics_record_model_to_domain(model) for model in record_models]

    async def find_by_date_range(
        self, start_date: date, end_date: date, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds all statistics records within a date range (inclusive) for a specific user."""
        # Ensure comparison is done only against the date part
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        stmt = (
            select(StatisticsRecordModel)
            .where(
                StatisticsRecordModel.user_id == user_id,
                StatisticsRecordModel.creation_date >= start_datetime,
                StatisticsRecordModel.creation_date <= end_datetime,
            )
            .options(selectinload(StatisticsRecordModel.category_statistics))
            .order_by(StatisticsRecordModel.creation_date.desc())
        )
        result = await self._session.execute(stmt)
        record_models = result.scalars().all()
        return [map_statistics_record_model_to_domain(model) for model in record_models]

    async def find_by_budget_id_and_date_range(
        self, budget_id: uuid.UUID, start_date: date, end_date: date, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds records for a specific budget and date range for a user."""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        stmt = (
            select(StatisticsRecordModel)
            .where(
                StatisticsRecordModel.budget_id == budget_id,
                StatisticsRecordModel.user_id == user_id,
                StatisticsRecordModel.creation_date >= start_datetime,
                StatisticsRecordModel.creation_date <= end_datetime,
            )
            .options(selectinload(StatisticsRecordModel.category_statistics))
            .order_by(StatisticsRecordModel.creation_date.desc())
        )
        result = await self._session.execute(stmt)
        record_models = result.scalars().all()
        return [map_statistics_record_model_to_domain(model) for model in record_models]
