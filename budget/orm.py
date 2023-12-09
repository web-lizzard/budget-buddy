from db.session import Base
from sqlalchemy import Column, ForeignKey, DECIMAL, String, UUID, DateTime, Table
from sqlalchemy.orm import relationship
from uuid import uuid4


budget_category_association_table = Table(
    "budget_category_association_table",
    Base.metadata,
    Column("budget_id", ForeignKey("budgets.id")),
    Column("category_id", ForeignKey("categories.id")),
)

budget_expense_association_table = Table(
    "budget_category_association_table",
    Base.metadata,
    Column("budget_id", ForeignKey("budgets.id")),
    Column("category_id", ForeignKey("categories.id")),
)


class CategoryTable(Base):
    __tablename__ = "categories"

    id = Column(UUID, primary_key=True, unique=True, index=True, default=uuid4)
    name = Column(String(length=100))


class ExpenseTable(Base):
    __tablename__ = "expenses"

    id = Column(UUID, primary_key=True, unique=True, index=True, default=uuid4)
    category_id = ForeignKey("categories.id")
    expense_date = Column(DateTime)

    _amount = Column(DECIMAL)


class BudgetTable(Base):
    __tablename__ = "budgets"

    id = Column(UUID, primary_key=True, unique=True, index=True, default=uuid4)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    expenses = relationship(secondary=budget_expense_association_table)
    categories = relationship(secondary=budget_category_association_table)

    _amount = Column(DECIMAL)
