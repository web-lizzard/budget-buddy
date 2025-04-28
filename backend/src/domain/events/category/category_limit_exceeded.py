from domain.events.domain_event import DomainEvent


class CategoryLimitExceeded(DomainEvent):
    category_id: str
    budget_id: str
    current_amount: int
    limit: int
