from decimal import Decimal
from typing import Self
from dataclasses import dataclass


@dataclass
class Money:
    """It's a int base abstraction for a currency"""

    currency_symbol: str
    current_amount: int = 0

    @classmethod
    def mint(cls, amount: Decimal | float, currency_symbol: str = "zł") -> Self:
        return cls(current_amount=int(amount * 100), currency_symbol=currency_symbol)

    def __str__(self) -> str:
        amount = self.current_amount / 100
        return f"{self.currency_symbol}{amount:.2f}"

    def __add__(self, other: Self):
        return Money(
            currency_symbol=self.currency_symbol,
            current_amount=self.current_amount + other.current_amount,
        )

    def __sub__(self, other: Self):
        return Money(
            currency_symbol=self.currency_symbol,
            current_amount=self.current_amount - other.current_amount,
        )

    def __truediv__(self, div: float | Decimal):
        return Money(
            current_amount=int(self.current_amount / div),
            currency_symbol=self.currency_symbol,
        )
