from datetime import datetime

from domain.events.domain_event import DomainEvent


class BudgetRenewed(DomainEvent):
    budget_id: str
    old_budget_id: str
    user_id: str
    start_date: datetime
    end_date: datetime
