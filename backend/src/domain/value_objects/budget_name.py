from dataclasses import dataclass

from domain.exceptions import (
    BudgetNameTooLongError,
    BudgetNameTooShortError,
    EmptyBudgetNameError,
)


@dataclass(frozen=True)
class BudgetName:
    """
    Value object representing a validated budget name.
    """

    _value: str

    # Constants for validation
    _MAX_LENGTH = 100
    _MIN_LENGTH = 3

    @property
    def value(self) -> str:
        return self._value

    def __post_init__(self):
        """
        Validate the budget name after initialization.

        Raises:
            EmptyBudgetNameError: If name is empty
            BudgetNameTooShortError: If name is shorter than MIN_LENGTH
            BudgetNameTooLongError: If name is longer than MAX_LENGTH
        """
        self._validate()

    def _validate(self) -> None:
        """
        Validate the budget name.

        Raises:
            EmptyBudgetNameError: If name is empty
            BudgetNameTooShortError: If name is shorter than MIN_LENGTH
            BudgetNameTooLongError: If name is longer than MAX_LENGTH
        """
        value = self._value.strip()

        if not value:
            raise EmptyBudgetNameError()

        if len(value) < self._MIN_LENGTH:
            raise BudgetNameTooShortError(self._MIN_LENGTH)

        if len(value) > self._MAX_LENGTH:
            raise BudgetNameTooLongError(self._MAX_LENGTH)

        object.__setattr__(self, "_value", value)

    def __str__(self) -> str:
        return self.value
