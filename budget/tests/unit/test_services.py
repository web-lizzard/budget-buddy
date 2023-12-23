from budget.domain.model import Budget, Category
import dto
from budget.adapters.repository import FakeBudgetRepository
from common.db.session import FakeSession
from budget.services import services
import pytest


def test_create_category():
    repository = FakeBudgetRepository(entities=[], categories=[])
    session = FakeSession()

    category = services.create_category(
        dto=dto.CreateProductDTO(name="Meal"), repository=repository, session=session
    )

    assert [category] == repository.list()


def test_budget_creation():
    category = Category(name="Meal")
    budget_repository = FakeBudgetRepository(entities=[], categories=[category])

    session = FakeSession()

    budget = services.create_budget(
        session=session,
        dto=dto.CreateBudgetDTO(categories_id=[str(category.id)], monthly_amount=2000),
        budget_repository=budget_repository,
    )

    assert budget_repository.list() == [budget]
    assert session.committed == True


def test_error_empty_categories():
    budget_repository = FakeBudgetRepository(entities=[], categories=[])
    session = FakeSession()

    with pytest.raises(services.CategoriesNotFound):
        services.create_budget(
            session=session,
            dto=dto.CreateBudgetDTO(categories_id=[], monthly_amount=2000),
            budget_repository=budget_repository,
        )


def test_associate_expense():
    category = Category(name="Meal")
    budget = Budget(categories=[category], _monthly_limit=3000)

    budget_repository = FakeBudgetRepository(entities=[budget], categories=[category])

    session = FakeSession()

    services.associate_expense_to_budgets(
        budget_repository=budget_repository,
        dto=dto.AddExpenseDTO(category_id=str(category.id), amount=400),
        session=session,
    )

    assert session.committed == True


def test_error_not_category():
    category = Category(name="Meal")
    budget = Budget(categories=[], _monthly_limit=3000)
    budget_repository = FakeBudgetRepository(entities=[budget], categories=[])
    session = FakeSession()

    with pytest.raises(services.CategoriesNotFound, match="Category not found"):
        services.associate_expense_to_budgets(
            budget_repository=budget_repository,
            dto=dto.AddExpenseDTO(category_id=str(category.id), amount=400),
            session=session,
        )
