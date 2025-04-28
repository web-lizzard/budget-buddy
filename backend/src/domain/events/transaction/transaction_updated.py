from datetime import datetime

from domain.events.domain_event import DomainEvent


class TransactionUpdated(DomainEvent):
    transaction_id: str
    category_id: str
    amount: int
    type: str
    date: datetime
