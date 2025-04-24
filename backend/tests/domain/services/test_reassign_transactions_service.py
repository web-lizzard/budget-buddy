import uuid
from datetime import datetime

from domain.aggregates.transaction import Transaction
from domain.services.reassign_transactions_service import ReassignTransactionsService
from domain.value_objects import (
    Money,
    MoveToOtherCategoryTransferPolicyInput,
    TransactionType,
)


class TestReassignTransactionsService:
    """Tests for the ReassignTransactionsService."""

    def test_reassign_transactions_updates_category_ids(self):
        """Test that the service updates transaction category IDs correctly."""
        # Arrange
        original_category_id = uuid.uuid4()
        target_category_id = uuid.uuid4()
        user_id = uuid.uuid4()

        # Create test transactions
        transactions = [
            Transaction(
                id=uuid.uuid4(),
                category_id=original_category_id,
                amount=Money(100, "USD"),
                transaction_type=TransactionType.EXPENSE,
                occurred_date=datetime.now(),
                user_id=user_id,
                description="Transaction 1",
            ),
            Transaction(
                id=uuid.uuid4(),
                category_id=original_category_id,
                amount=Money(200, "USD"),
                transaction_type=TransactionType.EXPENSE,
                occurred_date=datetime.now(),
                user_id=user_id,
                description="Transaction 2",
            ),
        ]

        # Create policy
        policy = MoveToOtherCategoryTransferPolicyInput(
            target_category_id=target_category_id
        )

        # Create service
        service = ReassignTransactionsService()

        # Act
        service.reassign_transactions(transactions, policy)

        # Assert
        for transaction in transactions:
            assert transaction.category_id == target_category_id

    def test_reassign_transactions_with_empty_list(self):
        """Test that the service handles an empty transaction list gracefully."""
        # Arrange
        target_category_id = uuid.uuid4()
        transactions = []
        policy = MoveToOtherCategoryTransferPolicyInput(
            target_category_id=target_category_id
        )
        service = ReassignTransactionsService()

        # Act & Assert (no exception should be raised)
        service.reassign_transactions(transactions, policy)
