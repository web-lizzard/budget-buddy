from domain.events.domain_event import DomainEvent


class CategoryAdded(DomainEvent):
    category_id: str
    budget_id: str
    name: str
    limit: int
