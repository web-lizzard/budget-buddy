import uuid
from dataclasses import dataclass
from datetime import datetime

from domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class StatisticsCalculated(DomainEvent):
    """Event indicating that statistics have been calculated for a budget."""

    # event_id: uuid.UUID # DomainEvent base class likely handles this implicitly or via occurred_on
    budget_id: uuid.UUID
    user_id: uuid.UUID
    statistics_record_id: uuid.UUID
    calculated_at: datetime  # Capture calculation time

    @staticmethod
    def create(
        budget_id: uuid.UUID,
        user_id: uuid.UUID,
        statistics_record_id: uuid.UUID,
    ) -> "StatisticsCalculated":
        """Factory method to create a new StatisticsCalculated event."""
        return StatisticsCalculated(
            # event_id=uuid.uuid4(), # Let base class handle if necessary
            budget_id=budget_id,
            user_id=user_id,
            statistics_record_id=statistics_record_id,
            calculated_at=datetime.now(),  # Use current time
        )
