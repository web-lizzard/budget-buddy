import uuid
from datetime import datetime

from ..domain_event import DomainEvent


class BudgetDeactivatedEvent(DomainEvent):
    """Event indicating that a budget has been deactivated."""

    budget_id: uuid.UUID
    deactivation_date: datetime  # Keep the deactivation date for context
