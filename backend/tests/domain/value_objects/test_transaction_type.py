import pytest
from domain.value_objects import TransactionType


class TestTransactionType:
    def test_enum_values(self):
        """Test that TransactionType enum has expected values."""
        assert TransactionType.EXPENSE.name == "EXPENSE"
        assert TransactionType.INCOME.name == "INCOME"
        assert len(list(TransactionType)) == 2

    @pytest.mark.parametrize("transaction_type, expected_str", [
        pytest.param(TransactionType.EXPENSE, "EXPENSE", id="expense_type"),
        pytest.param(TransactionType.INCOME, "INCOME", id="income_type"),
    ])
    def test_str_representation(self, transaction_type, expected_str):
        """Test string representation of TransactionType."""
        assert str(transaction_type) == expected_str

    @pytest.mark.parametrize("input_string, expected_type", [
        pytest.param("EXPENSE", TransactionType.EXPENSE, id="uppercase_expense"),
        pytest.param("INCOME", TransactionType.INCOME, id="uppercase_income"),
        pytest.param("expense", TransactionType.EXPENSE, id="lowercase_expense"),
        pytest.param("income", TransactionType.INCOME, id="lowercase_income"),
        pytest.param("ExPeNsE", TransactionType.EXPENSE, id="mixed_case"),
    ])
    def test_from_string_valid(self, input_string, expected_type):
        """Test creating TransactionType from valid string."""
        assert TransactionType.from_string(input_string) == expected_type

    def test_from_string_invalid(self):
        """Test that creating TransactionType from invalid string raises an exception."""
        with pytest.raises(ValueError) as exc:
            TransactionType.from_string("INVALID")
        
        assert "Invalid transaction type: INVALID" in str(exc.value)
        assert "Valid types are: EXPENSE, INCOME" in str(exc.value) or "Valid types are: INCOME, EXPENSE" in str(exc.value) 