from datetime import datetime

from domain.events.domain_event import DomainEvent


class BudgetDeactivated(DomainEvent):
    budget_id: str
    deactivation_date: datetime
