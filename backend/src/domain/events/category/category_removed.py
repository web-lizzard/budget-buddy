from domain.events.domain_event import DomainEvent


class CategoryRemoved(DomainEvent):
    category_id: str
    budget_id: str
    transfer_policy: str
