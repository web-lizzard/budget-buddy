from dataclasses import dataclass
from datetime import datetime

from domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class TransactionAdded(DomainEvent):
    transaction_id: str
    category_id: str
    amount: int
    type: str
    date: datetime

    def __post_init__(self):
        # Call parent __init__ since dataclass doesn't do it automatically
        super().__init__()
