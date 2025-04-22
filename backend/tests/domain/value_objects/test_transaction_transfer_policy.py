from uuid import UUID

import pytest
from domain.exceptions import InvalidTransferPolicyError
from domain.value_objects.transaction_transfer_policy import (
    DeleteTransactionsTransferPolicyInput,
    MoveToOtherCategoryTransferPolicyInput,
    TransactionTransferPolicyInput,
    TransactionTransferPolicyType,
)


class TestTransactionTransferPolicy:
    def test_delete_transactions_policy_input(self):
        """Test creating DELETE_TRANSACTIONS policy input."""
        policy = DeleteTransactionsTransferPolicyInput()
        assert policy.policy_type == TransactionTransferPolicyType.DELETE_TRANSACTIONS

    def test_move_to_other_category_policy_input(self):
        """Test creating MOVE_TO_OTHER_CATEGORY policy input."""
        category_id = UUID("12345678-1234-5678-1234-567812345678")
        policy = MoveToOtherCategoryTransferPolicyInput(target_category_id=category_id)
        assert (
            policy.policy_type == TransactionTransferPolicyType.MOVE_TO_OTHER_CATEGORY
        )
        assert policy.target_category_id == category_id

    def test_move_to_other_category_policy_input_with_none(self):
        """Test that creating MOVE_TO_OTHER_CATEGORY policy input with None raises an exception."""
        with pytest.raises(InvalidTransferPolicyError) as exc:
            MoveToOtherCategoryTransferPolicyInput(target_category_id=None)
        assert "Category ID cannot be None" in str(exc.value)

    @pytest.mark.parametrize(
        "policy1, policy2, should_be_equal",
        [
            pytest.param(
                DeleteTransactionsTransferPolicyInput(),
                DeleteTransactionsTransferPolicyInput(),
                True,
                id="same_delete_policy",
            ),
            pytest.param(
                MoveToOtherCategoryTransferPolicyInput(
                    target_category_id=UUID("12345678-1234-5678-1234-567812345678")
                ),
                MoveToOtherCategoryTransferPolicyInput(
                    target_category_id=UUID("12345678-1234-5678-1234-567812345678")
                ),
                True,
                id="same_move_policy",
            ),
            pytest.param(
                DeleteTransactionsTransferPolicyInput(),
                MoveToOtherCategoryTransferPolicyInput(
                    target_category_id=UUID("12345678-1234-5678-1234-567812345678")
                ),
                False,
                id="different_policy_types",
            ),
            pytest.param(
                MoveToOtherCategoryTransferPolicyInput(
                    target_category_id=UUID("12345678-1234-5678-1234-567812345678")
                ),
                MoveToOtherCategoryTransferPolicyInput(
                    target_category_id=UUID("87654321-4321-8765-4321-876543210987")
                ),
                False,
                id="different_target_ids",
            ),
            pytest.param(
                DeleteTransactionsTransferPolicyInput(),
                "not a policy object",
                False,
                id="different_object_types",
            ),
        ],
    )
    def test_equality(self, policy1, policy2, should_be_equal):
        """Test that TransactionTransferPolicyInput objects with same values are equal."""
        if should_be_equal:
            assert policy1 == policy2
        else:
            assert policy1 != policy2

    @pytest.mark.parametrize(
        "policy, expected_str",
        [
            pytest.param(
                DeleteTransactionsTransferPolicyInput(),
                "DELETE_TRANSACTIONS",
                id="delete_policy",
            ),
            pytest.param(
                MoveToOtherCategoryTransferPolicyInput(
                    target_category_id=UUID("12345678-1234-5678-1234-567812345678")
                ),
                f"MOVE_TO_OTHER_CATEGORY(target_id={UUID('12345678-1234-5678-1234-567812345678')})",
                id="move_policy",
            ),
        ],
    )
    def test_str_representation(self, policy, expected_str):
        """Test string representation of TransactionTransferPolicyInput."""
        assert str(policy) == expected_str

    def test_immutability(self):
        """Test that TransactionTransferPolicyInput objects are immutable."""
        policy = DeleteTransactionsTransferPolicyInput()

        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            policy.policy_type = TransactionTransferPolicyType.MOVE_TO_OTHER_CATEGORY

        # Test immutability of MoveToOtherCategoryTransferPolicyInput
        category_id = UUID("12345678-1234-5678-1234-567812345678")
        move_policy = MoveToOtherCategoryTransferPolicyInput(
            target_category_id=category_id
        )

        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            move_policy.target_category_id = UUID(
                "87654321-4321-8765-4321-876543210987"
            )
