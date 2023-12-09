from datetime import datetime
from budget.budget import Budget, Category, associate_expense, Expense
from monetary.money import Money
from sqlalchemy import insert
from .model import category_table


def test_create_category(session):
    session.execute(insert(category_table).values(name="Meal"))
    session.commit()

    expected = [Category("Meal")]

    assert session.query(Category).all() == expected


def test_create_budget(session):
    category = Category(name="meal")
    budget = Budget(monthly_limit=Money.mint(4000), categories=[category])

    session.add(budget)
    session.commit()

    assert session.query(Budget).all() == [budget]
    assert session.query(Category).all() == [category]


def test_associate_expense(session):
    category = Category(name="Meal")
    budget = Budget(monthly_limit=Money.mint(4000), categories=[category])
    expense = Expense(category=category, amount=Money.mint(400))

    associate_expense(budgets=[budget], expense=expense)

    session.add(budget)
    session.commit()

    assert session.query(Budget).all() == [budget]
    assert session.query(Category).all() == [category]
    assert session.query(Expense).all() == [expense]
