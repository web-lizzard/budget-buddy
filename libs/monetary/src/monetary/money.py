from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Self


class Currency(Enum):
    USD = "USD"
    PLN = "PLN"


@dataclass(frozen=True)
class Money:
    _amount_in_subunits: int
    _currency: Currency

    @property
    def amount(self) -> int:
        return self._amount_in_subunits

    @property
    def amount_in_main_unit(self) -> Decimal:
        return Decimal(self._amount_in_subunits) / Decimal(100)

    @property
    def currency(self) -> Currency:
        return self._currency

    @classmethod
    def mint(cls, amount: float, currency: Currency) -> Self:
        _amount_in_subunits = Decimal(str(amount)) * Decimal(100)
        return cls(_amount_in_subunits=int(_amount_in_subunits), _currency=currency)

    def __str__(self) -> str:
        return f"{self.amount_in_main_unit} {self._currency.value}"

    def __add__(self, other: Self) -> Self:
        if self._currency != other._currency:
            raise ValueError("Cannot add money with different currencies")

        return Money(self._amount_in_subunits + other._amount_in_subunits, self._currency)

    def __sub__(self, other: Self) -> Self:
        if self._currency != other._currency:
            raise ValueError("Cannot subtract money with different currencies")

        return Money(self._amount_in_subunits - other._amount_in_subunits, self._currency)

    def __mul__(self, multiplier: int) -> Self:
        return Money(self._amount_in_subunits * multiplier, self._currency)

    def __truediv__(self, divisor: int) -> Self:
        return Money(self._amount_in_subunits // divisor, self._currency)

    def __eq__(self, other: Self) -> bool:
        return (
            self._amount_in_subunits == other._amount_in_subunits
            and self._currency == other._currency
        )

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: Self) -> bool:
        if self._currency != other._currency:
            raise ValueError("Cannot compare money with different currencies")

        return self._amount_in_subunits < other._amount_in_subunits

    def __le__(self, other: Self) -> bool:
        if self._currency != other._currency:
            raise ValueError("Cannot compare money with different currencies")

        return self._amount_in_subunits <= other._amount_in_subunits

    def __gt__(self, other: Self) -> bool:
        if self._currency != other._currency:
            raise ValueError("Cannot compare money with different currencies")

        return self._amount_in_subunits > other._amount_in_subunits

    def __ge__(self, other: Self) -> bool:
        if self._currency != other._currency:
            raise ValueError("Cannot compare money with different currencies")

        return self._amount_in_subunits >= other._amount_in_subunits
