from datetime import datetime

from domain.events.domain_event import DomainEvent


class BudgetCreated(DomainEvent):
    budget_id: str
    user_id: str
    total_limit: int
    start_date: datetime
    strategy: str
    name: str
    end_date: datetime
