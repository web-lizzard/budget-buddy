from uuid import UUID

from pydantic import BaseModel

from domain.events.domain_event import DomainEvent


class TransactionDeletedEvent(DomainEvent, BaseModel):
    """Event representing a transaction that has been deleted."""

    transaction_id: UUID
    budget_id: UUID
    user_id: UUID
