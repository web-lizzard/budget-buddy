from uuid import UUID

from adapters.outbound.persistence.sql_alchemy.models import (
    BudgetModel,
    CategoryModel,
    ORMBudgetStrategy,
    ORMLimit,
    ORMMoney,
)
from domain.aggregates.budget import Budget
from domain.entities.category import Category
from domain.value_objects import BudgetName, CategoryName


# --- Category Mappers ---
def map_category_model_to_domain(model: CategoryModel) -> Category:
    """Maps CategoryModel SQLAlchemy object to Category domain entity."""
    return Category(
        id=model.id,
        budget_id=model.budget_id,
        name=CategoryName(model.name),
        limit=model.limit,
    )


def map_category_domain_to_model(domain: Category, user_id: UUID) -> CategoryModel:
    """Maps Category domain entity to CategoryModel SQLAlchemy object."""
    return CategoryModel(
        id=domain.id,
        budget_id=domain.budget_id,
        name=domain.name.value,
        user_id=user_id,
        _limit_amount=domain.limit.value.amount,
        _limit_currency=domain.limit.value.currency,
        limit=ORMLimit(
            value=ORMMoney(
                amount=domain.limit.value.amount,
                currency=domain.limit.value.currency,
            ),
        ),
    )


# --- Budget Mappers ---
def map_budget_model_to_domain(model: BudgetModel) -> Budget:
    """Maps BudgetModel SQLAlchemy object to Budget domain aggregate."""
    return Budget(
        id=model.id,
        user_id=model.user_id,
        total_limit=model.total_limit,
        start_date=model.start_date,
        end_date=model.end_date,
        strategy_input=model.strategy.strategy_input,
        name=BudgetName(model.name),
        categories=[
            map_category_model_to_domain(cat_model) for cat_model in model.categories
        ],
        deactivation_date=model.deactivation_date,
    )


def map_budget_domain_to_model(
    domain: Budget, existing_model: BudgetModel | None = None
) -> BudgetModel:
    """Maps Budget domain aggregate to BudgetModel SQLAlchemy object.

    Args:
        domain: The Budget domain aggregate.
        existing_model: Optional existing BudgetModel to update.
                          If provided, helps preserve existing model state like created_at.
    """
    # Create or update the model
    model = existing_model or BudgetModel()

    model.id = domain.id
    model.user_id = domain.user_id
    model.name = domain.name.value

    model._total_limit_amount = domain.total_limit.value.amount
    model._total_limit_currency = domain.total_limit.value.currency
    model.total_limit = ORMLimit(
        value=ORMMoney(
            amount=domain.total_limit.value.amount,
            currency=domain.total_limit.value.currency,
        ),
    )

    orm_strategy = ORMBudgetStrategy(domain.strategy_input)
    model._strategy_type_db, model._strategy_parameters = (
        orm_strategy.__composite_values__()
    )
    model.strategy = orm_strategy

    model.start_date = domain.start_date
    model.end_date = domain.end_date
    model.deactivation_date = domain.deactivation_date

    model.categories = [
        map_category_domain_to_model(cat_domain, model.user_id)
        for cat_domain in domain.categories
    ]

    return model
