from datetime import datetime

from domain.events.domain_event import DomainEvent


class TransactionAdded(DomainEvent):
    transaction_id: str
    category_id: str
    budget_id: str
    amount: int
    type: str
    date: datetime
    user_id: str
