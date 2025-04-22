from dataclasses import dataclass

from domain.exceptions import (
    CategoryNameTooLongError,
    CategoryNameTooShortError,
    EmptyCategoryNameError,
)


@dataclass(frozen=True)
class CategoryName:
    """
    Value object representing a validated category name.
    """

    _value: str

    # Constants for validation
    _MAX_LENGTH = 255
    _MIN_LENGTH = 3

    @property
    def value(self) -> str:
        return self._value

    def __post_init__(self):
        """
        Validate the category name after initialization.

        Raises:
            InvalidCategoryNameTypeError: If name is not a string
            EmptyCategoryNameError: If name is empty
            CategoryNameTooShortError: If name is shorter than MIN_LENGTH
            CategoryNameTooLongError: If name is longer than MAX_LENGTH
        """
        self._validate()

    def _validate(self) -> None:
        """
        Validate the category name.

        Raises:
            InvalidCategoryNameTypeError: If name is not a string
            EmptyCategoryNameError: If name is empty
            CategoryNameTooShortError: If name is shorter than MIN_LENGTH
            CategoryNameTooLongError: If name is longer than MAX_LENGTH
        """
        value = self._value.strip()

        if not value:
            raise EmptyCategoryNameError()

        if len(value) < self._MIN_LENGTH:
            raise CategoryNameTooShortError(self._MIN_LENGTH)

        if len(value) > self._MAX_LENGTH:
            raise CategoryNameTooLongError(self._MAX_LENGTH)

        object.__setattr__(self, "_value", value)

    def __str__(self) -> str:
        return self.value
