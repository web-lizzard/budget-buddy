from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from domain.exceptions import InvalidStrategyParameterError


class BudgetStrategyType(Enum):
    """Enum representing budget strategy types."""

    MONTHLY = "monthly"
    YEARLY = "yearly"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BudgetStrategyInput(ABC):
    """
    Abstract value object defining input parameters for a budget strategy.
    """

    @property
    @abstractmethod
    def strategy_type(self) -> BudgetStrategyType:
        """Return the strategy type."""
        pass


@dataclass(frozen=True)
class MonthlyBudgetStrategyInput(BudgetStrategyInput):
    """Monthly budget strategy input parameters."""

    start_day: int = 1

    def __post_init__(self):
        """Validate parameters after initialization."""
        if (
            not isinstance(self.start_day, int)
            or self.start_day < 1
            or self.start_day > 28
        ):
            raise InvalidStrategyParameterError("start_day", self.start_day)

    @property
    def strategy_type(self) -> BudgetStrategyType:
        return BudgetStrategyType.MONTHLY

    def __str__(self) -> str:
        return f"{self.strategy_type} (start_day: {self.start_day})"


@dataclass(frozen=True)
class YearlyBudgetStrategyInput(BudgetStrategyInput):
    """Yearly budget strategy input parameters."""

    start_month: int = 1
    start_day: int = 1

    def __post_init__(self):
        """Validate parameters after initialization."""
        if (
            not isinstance(self.start_month, int)
            or self.start_month < 1
            or self.start_month > 12
        ):
            raise InvalidStrategyParameterError("start_month", self.start_month)

        if (
            not isinstance(self.start_day, int)
            or self.start_day < 1
            or self.start_day > 28
        ):
            raise InvalidStrategyParameterError("start_day", self.start_day)

    @property
    def strategy_type(self) -> BudgetStrategyType:
        return BudgetStrategyType.YEARLY

    def __str__(self) -> str:
        return f"{self.strategy_type} (start_month: {self.start_month}, start_day: {self.start_day})"
