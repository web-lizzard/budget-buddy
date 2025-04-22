from enum import Enum, auto


class TransactionType(Enum):
    """Enum representing transaction types."""
    
    EXPENSE = auto()
    INCOME = auto()
    
    def __str__(self) -> str:
        return self.name
    
    @classmethod
    def from_string(cls, value: str) -> 'TransactionType':
        """
        Create TransactionType from string.
        
        Args:
            value: String representation of transaction type
            
        Returns:
            TransactionType enum value
            
        Raises:
            ValueError: If value is not a valid transaction type
        """
        try:
            return cls[value.upper()]
        except KeyError:
            valid_types = ', '.join([t.name for t in cls])
            raise ValueError(f"Invalid transaction type: {value}. Valid types are: {valid_types}") 