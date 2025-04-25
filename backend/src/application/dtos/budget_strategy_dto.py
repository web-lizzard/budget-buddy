from pydantic import Field

from .dto import DTO


class BudgetStrategyDTO(DTO):
    type: str  # e.g., 'monthly' or 'yearly'
    parameters: dict = Field(default_factory=dict)
