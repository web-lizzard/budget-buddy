from application.dtos import (
    BudgetDTO,
    BudgetStrategyDTO,
    CategoryDTO,
    CategoryStatisticsRecordDTO,
    MoneyDTO,
    StatisticsRecordDTO,
    TransactionDTO,
    TransactionTypeEnum,
)
from domain.aggregates.budget import Budget
from domain.aggregates.statistics_record import (
    CategoryStatisticsRecord,
    StatisticsRecord,
)
from domain.aggregates.transaction import Transaction
from domain.entities.category import Category
from domain.value_objects import Money

# Helper functions to map domain objects to DTOs


def map_money_to_dto(money: Money) -> MoneyDTO:
    """Maps Money value object to MoneyDTO."""
    return MoneyDTO(amount=money.to_float(), currency=money.currency)


def map_category_to_dto(category: Category) -> CategoryDTO:
    """Maps Category domain object to CategoryDTO."""

    limit_money = category.limit.value

    return CategoryDTO(
        id=category.id,
        budget_id=category.budget_id,
        name=category.name.value,
        limit=map_money_to_dto(limit_money),
    )


def map_budget_to_dto(budget: Budget) -> BudgetDTO:
    """Maps Budget domain object to BudgetDTO."""
    strategy_type = budget.strategy_input.strategy_type

    return BudgetDTO(
        id=budget.id,
        user_id=budget.user_id,
        total_limit=map_money_to_dto(budget.total_limit.value),
        currency=budget.currency,  # Assuming currency is directly on budget domain object
        start_date=budget.start_date,
        end_date=budget.end_date,
        strategy=BudgetStrategyDTO(
            type=str(strategy_type),
        ),
        name=budget.name.value,
        deactivation_date=budget.deactivation_date,
        categories=[
            map_category_to_dto(cat) for cat in budget.categories
        ],  # Assuming budget.categories exists
    )


def map_transaction_to_dto(transaction: Transaction) -> TransactionDTO:
    """Maps Transaction domain object to TransactionDTO."""

    transaction_type = transaction.transaction_type
    transaction_type_dto = TransactionTypeEnum(str(transaction_type).upper())

    return TransactionDTO(
        id=transaction.id,
        category_id=transaction.category_id,
        amount=map_money_to_dto(transaction.amount),
        transaction_type=transaction_type_dto,
        occurred_date=transaction.occurred_date,
        description=transaction.description,
        user_id=transaction.user_id,
    )


def map_category_stats_to_dto(
    category_stats: CategoryStatisticsRecord,
) -> CategoryStatisticsRecordDTO:
    """Maps CategoryStatisticsRecord domain object to CategoryStatisticsRecordDTO."""
    return CategoryStatisticsRecordDTO(
        id=category_stats.id,
        category_id=category_stats.category_id,
        current_balance=map_money_to_dto(category_stats.current_balance),
        daily_available_amount=map_money_to_dto(category_stats.daily_available_amount),
        daily_average=map_money_to_dto(category_stats.daily_average),
        used_limit=map_money_to_dto(category_stats.used_limit),
    )


def map_statistics_record_to_dto(stats: StatisticsRecord) -> StatisticsRecordDTO:
    """Maps StatisticsRecord domain object to StatisticsRecordDTO."""
    return StatisticsRecordDTO(
        id=stats.id,
        user_id=stats.user_id,
        budget_id=stats.budget_id,
        current_balance=map_money_to_dto(stats.current_balance),
        daily_available_amount=map_money_to_dto(stats.daily_available_amount),
        daily_average=map_money_to_dto(stats.daily_average),
        used_limit=map_money_to_dto(stats.used_limit),
        creation_date=stats.creation_date,
        categories_statistics=[
            map_category_stats_to_dto(cat_stat)
            for cat_stat in stats.categories_statistics
        ],
    )
