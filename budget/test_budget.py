from .budget import Category, Expense, Budget, associate_expense


def create_budget() -> tuple[Budget, Expense, Category]:
    category = Category(name="Meal")
    budget = Budget(_monthly_limit=2000, categories=[category])
    expense = Expense(category=category, _amount=25.4)

    return (budget, expense, category)


def test_associate_expense():
    budget, expense, _ = create_budget()
    second_category = Category(name="name")
    second_budget = Budget(
        _monthly_limit=2000,
        categories=[second_category],
    )

    associate_expense(expense=expense, budgets=[budget, second_budget])

    assert expense in budget.expenses
    assert expense not in second_budget.expenses


def test_compute_expensed_in_budget():
    budget, expense, category = create_budget()
    second_expense = Expense(category=category, _amount=40)

    associate_expense(expense=expense, budgets=[budget])
    associate_expense(expense=second_expense, budgets=[budget])

    assert budget.computed_expenses.current_amount == 6540


def test_current_balance():
    budget, expense, _ = create_budget()

    associate_expense(expense=expense, budgets=[budget])

    assert budget.current_balance.current_amount == 197460
