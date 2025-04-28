import datetime
import uuid

from adapters.outbound.persistence.sql_alchemy.models import (
    CategoryStatisticsRecordModel,
    ORMMoney,
    StatisticsRecordModel,
)
from domain.aggregates.statistics_record import StatisticsRecord
from domain.entities import CategoryStatisticsRecord


def map_category_statistics_record_model_to_domain(
    model: CategoryStatisticsRecordModel,
) -> CategoryStatisticsRecord:
    """Maps CategoryStatisticsRecordModel SQLAlchemy object to CategoryStatisticsRecord domain entity."""
    return CategoryStatisticsRecord(
        id=model.id,
        category_id=model.category_id,
        current_balance=model.current_balance,
        daily_available_amount=model.daily_available_amount,
        daily_average=model.daily_average,
        used_limit=model.used_limit,
    )


def map_category_statistics_record_domain_to_model(
    domain: CategoryStatisticsRecord,
    statistics_record_model_id: uuid.UUID,
    user_id: uuid.UUID,
    creation_date: datetime.datetime,
) -> CategoryStatisticsRecordModel:
    """Maps CategoryStatisticsRecord domain entity to CategoryStatisticsRecordModel SQLAlchemy object."""
    # TODO: statistics_record_model_id and user_id might be needed for consistency
    return CategoryStatisticsRecordModel(
        id=domain.id,
        statistics_record_id=statistics_record_model_id,
        category_id=domain.category_id,
        user_id=user_id,
        _cat_current_balance_amount=domain.current_balance.amount,
        _cat_current_balance_currency=domain.current_balance.currency,
        current_balance=ORMMoney(
            amount=domain.current_balance.amount,
            currency=domain.current_balance.currency,
        ),
        _cat_daily_available_amount_amount=domain.daily_available_amount.amount,
        _cat_daily_available_amount_currency=domain.daily_available_amount.currency,
        daily_available_amount=ORMMoney(
            amount=domain.daily_available_amount.amount,
            currency=domain.daily_available_amount.currency,
        ),
        _cat_daily_average_amount=domain.daily_average.amount,
        _cat_daily_average_currency=domain.daily_average.currency,
        daily_average=ORMMoney(
            amount=domain.daily_average.amount,
            currency=domain.daily_average.currency,
        ),
        _cat_used_limit_amount=domain.used_limit.amount,
        _cat_used_limit_currency=domain.used_limit.currency,
        used_limit=ORMMoney(
            amount=domain.used_limit.amount,
            currency=domain.used_limit.currency,
        ),
        created_at=creation_date,
    )


def map_statistics_record_model_to_domain(
    model: StatisticsRecordModel,
) -> StatisticsRecord:
    """Maps StatisticsRecordModel SQLAlchemy object to StatisticsRecord domain aggregate."""
    return StatisticsRecord(
        id=model.id,
        user_id=model.user_id,
        budget_id=model.budget_id,
        current_balance=model.current_balance,
        daily_available_amount=model.daily_available_amount,
        daily_average=model.daily_average,
        used_limit=model.used_limit,
        creation_date=model.creation_date,
        categories_statistics=[
            map_category_statistics_record_model_to_domain(cs)
            for cs in model.category_statistics
        ],
    )


def map_statistics_record_domain_to_model(
    domain: StatisticsRecord,
) -> StatisticsRecordModel:
    """Maps StatisticsRecord domain aggregate to StatisticsRecordModel SQLAlchemy object."""
    model = StatisticsRecordModel(
        id=domain.id,
        user_id=domain.user_id,
        budget_id=domain.budget_id,
        _current_balance_amount=domain.current_balance.amount,
        _current_balance_currency=domain.current_balance.currency,
        current_balance=ORMMoney(
            amount=domain.current_balance.amount,
            currency=domain.current_balance.currency,
        ),
        _daily_available_amount_amount=domain.daily_available_amount.amount,
        _daily_available_amount_currency=domain.daily_available_amount.currency,
        daily_available_amount=ORMMoney(
            amount=domain.daily_available_amount.amount,
            currency=domain.daily_available_amount.currency,
        ),
        _daily_average_amount=domain.daily_average.amount,
        _daily_average_currency=domain.daily_average.currency,
        daily_average=ORMMoney(
            amount=domain.daily_average.amount,
            currency=domain.daily_average.currency,
        ),
        _used_limit_amount=domain.used_limit.amount,
        _used_limit_currency=domain.used_limit.currency,
        used_limit=ORMMoney(
            amount=domain.used_limit.amount, currency=domain.used_limit.currency
        ),
        category_statistics=[
            map_category_statistics_record_domain_to_model(
                cs, domain.id, domain.user_id, domain.creation_date
            )
            for cs in domain.categories_statistics
        ],
        created_at=domain.creation_date,
        creation_date=domain.creation_date,
    )
    return model
