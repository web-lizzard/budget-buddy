from .model import Budget, Category
import dto
from db.repository import FakeRepository
from db.session import FakeSession
from budget import services
import pytest


def test_create_category():
    repository = FakeRepository([])
    session = FakeSession()

    category = services.create_category(
        dto=dto.CreateProductDTO(name="Meal"), repository=repository, session=session
    )

    assert [category] == repository.list()


def test_budget_creation():
    budget_repository = FakeRepository([])
    category = Category(name="Meal")
    category_repository = FakeRepository([category])

    session = FakeSession()

    budget = services.create_budget(
        session=session,
        dto=dto.CreateBudgetDTO(categories_id=[str(category.id)], monthly_amount=2000),
        budget_repository=budget_repository,
        categories_repository=category_repository,
    )

    assert budget_repository.list() == [budget]
    assert session.committed == True


def test_error_empty_categories():
    budget_repository = FakeRepository([])
    category_repository = FakeRepository([])
    session = FakeSession()

    with pytest.raises(
        services.CategoriesNotFound,
        match="Impossible to create budget without categories",
    ):
        services.create_budget(
            session=session,
            dto=dto.CreateBudgetDTO(categories_id=[], monthly_amount=2000),
            budget_repository=budget_repository,
            categories_repository=category_repository,
        )


def test_associate_expense():
    category = Category(name="Meal")
    budget = Budget(categories=[category], _monthly_limit=3000)

    budget_repository = FakeRepository([budget])
    category_repository = FakeRepository([category])
    session = FakeSession()

    services.associate_expense_to_budgets(
        budget_repository=budget_repository,
        category_repository=category_repository,
        dto=dto.AddExpenseDTO(category_id=str(category.id), amount=400),
        session=session,
    )

    assert session.committed == True


def test_error_not_category():
    category = Category(name="Meal")
    budget = Budget(categories=[], _monthly_limit=3000)

    budget_repository = FakeRepository([budget])
    category_repository = FakeRepository([])
    session = FakeSession()

    with pytest.raises(services.CategoriesNotFound, match="Category not found"):
        services.associate_expense_to_budgets(
            budget_repository=budget_repository,
            category_repository=category_repository,
            dto=dto.AddExpenseDTO(category_id=str(category.id), amount=400),
            session=session,
        )
