import uuid
from dataclasses import dataclass
from datetime import datetime

from domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class StatisticsCalculated(DomainEvent):
    """Event indicating that statistics have been calculated for a budget."""

    budget_id: uuid.UUID
    user_id: uuid.UUID
    statistics_record_id: uuid.UUID
    calculated_at: datetime
