import uuid
from dataclasses import dataclass, field
from datetime import datetime

from domain.entities import CategoryStatisticsRecord
from domain.value_objects import Money


@dataclass
class StatisticsRecord:
    """
    Represents overall financial statistics resulting from budget operations.
    Generated independently to provide an overview of budget performance and trends.
    """

    # Fields without defaults first
    user_id: uuid.UUID
    budget_id: uuid.UUID
    current_balance: Money
    daily_available_amount: Money
    daily_average: Money
    used_limit: Money

    # Fields with defaults
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    # Re-add creation_date
    creation_date: datetime = field(default_factory=datetime.now)
    # Use correct field name and type hint
    categories_statistics: list[CategoryStatisticsRecord] = field(default_factory=list)
