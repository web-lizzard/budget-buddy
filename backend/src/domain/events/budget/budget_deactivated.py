from dataclasses import dataclass
from datetime import datetime

from domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class BudgetDeactivated(DomainEvent):
    budget_id: str
    deactivation_date: datetime

    def __post_init__(self):
        # Call parent __init__ since dataclass doesn't do it automatically
        super().__init__()
