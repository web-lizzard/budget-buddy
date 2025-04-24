from uuid import UUID

from domain.events.domain_event import DomainEvent


class TransactionDeletedEvent(DomainEvent):
    """Event representing a transaction that has been deleted."""

    def __init__(
        self,
        transaction_id: UUID,
        budget_id: UUID,
        user_id: UUID,
    ):
        """Initialize the transaction deleted event.

        Args:
            transaction_id: ID of the deleted transaction
            budget_id: ID of the budget containing the transaction
            user_id: ID of the user who made the change
        """
        self.transaction_id = transaction_id
        self.budget_id = budget_id
        self.user_id = user_id
