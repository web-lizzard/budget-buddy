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
    id: uuid.UUID
    transaction_id: uuid.UUID | None = None  # Add optional transaction_id
    # Re-add creation_date
    creation_date: datetime = field(default_factory=datetime.now)
    # Use correct field name and type hint
    categories_statistics: list[CategoryStatisticsRecord] = field(default_factory=list)

    def set_transaction_id(self, transaction_id: uuid.UUID) -> None:
        """
        Sets the transaction ID for the statistics record.

        Args:
            transaction_id (uuid.UUID): The unique identifier of the transaction
            associated with this statistics record.
        """
        self.transaction_id = transaction_id

    def set_id(self, id: uuid.UUID) -> None:
        """
        Sets the ID for the statistics record.
        """
        self.id = id

    def set_creation_date(self, creation_date: datetime) -> None:
        """
        Sets the creation date for the statistics record.
        """
        self.creation_date = creation_date
