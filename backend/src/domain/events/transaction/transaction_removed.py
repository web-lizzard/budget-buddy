from dataclasses import dataclass

from domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class TransactionRemoved(DomainEvent):
    transaction_id: str
    category_id: str

    def __post_init__(self):
        # Call parent __init__ since dataclass doesn't do it automatically
        super().__init__()
