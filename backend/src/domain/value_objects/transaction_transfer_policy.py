from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID

from domain.exceptions import InvalidTransferPolicyError


class TransactionTransferPolicyType(Enum):
    """Enum representing transaction transfer policy types."""

    DELETE_TRANSACTIONS = auto()
    MOVE_TO_OTHER_CATEGORY = auto()


@dataclass(frozen=True)
class TransactionTransferPolicyInput(ABC):
    """
    Abstract value object defining how transactions are handled when a category is deleted.
    """

    @property
    @abstractmethod
    def policy_type(self) -> TransactionTransferPolicyType:
        """Return the policy type."""
        pass


@dataclass(frozen=True)
class DeleteTransactionsTransferPolicyInput(TransactionTransferPolicyInput):
    """Policy input for deleting transactions."""

    @property
    def policy_type(self) -> TransactionTransferPolicyType:
        return TransactionTransferPolicyType.DELETE_TRANSACTIONS

    def __str__(self) -> str:
        return "DELETE_TRANSACTIONS"


@dataclass(frozen=True)
class MoveToOtherCategoryTransferPolicyInput(TransactionTransferPolicyInput):
    """Policy input for moving transactions to another category."""

    target_category_id: UUID | None

    def __post_init__(self):
        """Validate policy configuration after initialization."""
        if self.target_category_id is None:
            raise InvalidTransferPolicyError("Category ID cannot be None")

    @property
    def policy_type(self) -> TransactionTransferPolicyType:
        return TransactionTransferPolicyType.MOVE_TO_OTHER_CATEGORY

    def __str__(self) -> str:
        return f"MOVE_TO_OTHER_CATEGORY(target_id={self.target_category_id})"
