from domain.events.domain_event import DomainEvent


class StatisticsUpdated(DomainEvent):
    statistics_id: str
    budget_id: str
    category_id: str
    current_balance: float
    daily_available_amount: float
