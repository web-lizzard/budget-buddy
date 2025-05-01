from uuid import UUID

from pydantic import BaseModel

from domain.events.domain_event import DomainEvent
from domain.value_objects import Money, TransactionType


class TransactionEditedEvent(DomainEvent, BaseModel):
    """Event representing a transaction that has been edited."""

    transaction_id: UUID
    budget_id: UUID
    user_id: UUID
    category_id: UUID
    amount: Money
    transaction_type: TransactionType
    description: str | None = None
