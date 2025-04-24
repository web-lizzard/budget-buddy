from typing import Optional
from uuid import UUID

from domain.events.domain_event import DomainEvent
from domain.value_objects import Money, TransactionType


class TransactionEditedEvent(DomainEvent):
    """Event representing a transaction that has been edited."""

    def __init__(
        self,
        transaction_id: UUID,
        budget_id: UUID,
        user_id: UUID,
        category_id: UUID,
        amount: Money,
        transaction_type: TransactionType,
        description: Optional[str] = None,
    ):
        """Initialize the transaction edited event.

        Args:
            transaction_id: ID of the edited transaction
            budget_id: ID of the budget containing the transaction
            user_id: ID of the user who made the change
            category_id: New category ID
            amount: New transaction amount
            transaction_type: New transaction type
            description: New transaction description
        """
        self.transaction_id = transaction_id
        self.budget_id = budget_id
        self.user_id = user_id
        self.category_id = category_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
