from dataclasses import dataclass

from domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class StatisticsUpdated(DomainEvent):
    statistics_id: str
    budget_id: str
    category_id: str
    current_balance: float
    daily_available_amount: float

    def __post_init__(self):
        # Call parent __init__ since dataclass doesn't do it automatically
        super().__init__()
