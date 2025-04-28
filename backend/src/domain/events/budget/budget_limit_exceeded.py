from domain.events.domain_event import DomainEvent


class BudgetLimitExceeded(DomainEvent):
    budget_id: str
    current_amount: int
    limit: int
