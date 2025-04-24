from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.value_objects import BudgetStrategyInput

from .command import Command


@dataclass(frozen=True)
class CategoryData:
    """Input data for a category in a budget creation command."""

    name: str
    limit: float


@dataclass(frozen=True)
class CreateBudgetCommand(Command):
    """Command for creating a new budget."""

    user_id: UUID
    total_limit: float
    currency: str
    strategy_input: BudgetStrategyInput
    start_date: datetime
    categories: list[CategoryData]
