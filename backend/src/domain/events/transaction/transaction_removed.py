from domain.events.domain_event import DomainEvent


class TransactionRemoved(DomainEvent):
    transaction_id: str
    category_id: str
    budget_id: str
    user_id: str
