from dataclasses import dataclass
from decimal import Decimal
from typing import Union

from domain.exceptions import InvalidCurrencyError, CurrencyMismatchError


@dataclass(frozen=True)
class Money:
    """
    Value object representing an amount in a specific currency.
    """
    amount: int
    currency: str
    
    def __post_init__(self):
        """Validate currency after initialization."""
        if not isinstance(self.currency, str) or not self.currency or len(self.currency) != 3:
            raise InvalidCurrencyError(self.currency)
        
        # Convert currency to uppercase
        object.__setattr__(self, 'currency', self.currency.upper())
    
    def __str__(self) -> str:
        major_units = abs(self.amount) // 100
        minor_units = abs(self.amount) % 100
        sign = "-" if self.amount < 0 else ""
        return f"{sign}{major_units}.{minor_units:02d} {self.currency}"
    
    def add(self, money: 'Money') -> 'Money':
        """
        Add money amounts.
        
        Args:
            money: Money to add
            
        Returns:
            A new Money object with the sum
            
        Raises:
            CurrencyMismatchError: If currencies don't match
        """
        self._ensure_same_currency(money)
        return Money(self.amount + money.amount, self.currency)
    
    def subtract(self, money: 'Money') -> 'Money':
        """
        Subtract money amount.
        
        Args:
            money: Money to subtract
            
        Returns:
            A new Money object with the difference
            
        Raises:
            CurrencyMismatchError: If currencies don't match
        """
        self._ensure_same_currency(money)
        return Money(self.amount - money.amount, self.currency)
    
    def multiply_by(self, factor: Union[int, float, Decimal]) -> 'Money':
        """
        Multiply amount by a factor.
        
        Args:
            factor: Multiplication factor
            
        Returns:
            A new Money object with the multiplied amount
        """
        # Convert to Decimal for precise calculation
        decimal_factor = Decimal(str(factor))
        new_amount = int(Decimal(self.amount) * decimal_factor)
        
        return Money(new_amount, self.currency)
    
    def divide_by(self, divisor: Union[int, float, Decimal]) -> 'Money':
        """
        Divide amount by a divisor.
        
        Args:
            divisor: Division factor
            
        Returns:
            A new Money object with the divided amount
            
        Raises:
            ValueError: If divisor is zero
        """
        if divisor == 0:
            raise ValueError("Division by zero is not allowed")
        
        # Convert to Decimal for precise calculation
        decimal_divisor = Decimal(str(divisor))
        new_amount = int(Decimal(self.amount) / decimal_divisor)
        
        return Money(new_amount, self.currency)
    
    def _ensure_same_currency(self, other: 'Money') -> None:
        """
        Ensure that currencies match.
        
        Args:
            other: Other Money object
            
        Raises:
            CurrencyMismatchError: If currencies don't match
        """
        if self.currency != other.currency:
            raise CurrencyMismatchError(self.currency, other.currency)
    
    @staticmethod
    def mint(amount: float, currency: str) -> 'Money':
        """
        Create a Money object from a float amount.
        
        Args:
            amount: Amount in major units (e.g. dollars)
            currency: Currency code
            
        Returns:
            Money object
        """
        # Convert to smallest currency unit (e.g. cents)
        amount_in_cents = int(Decimal(str(amount)) * 100)
        
        return Money(amount_in_cents, currency) 