from datetime import datetime

from domain.events.domain_event import DomainEvent


class BudgetExpired(DomainEvent):
    budget_id: str
    end_date: datetime
