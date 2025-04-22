from typing import Any

import pytest
from domain.exceptions import CurrencyMismatchError, InvalidLimitValueError
from domain.value_objects.limit import Limit
from domain.value_objects.money import Money


class TestLimit:
    def test_init_valid_limit(self):
        """Test creating a valid Limit object."""
        money = Money(1000, "USD")
        limit = Limit(money)

        assert limit.value == money
        assert limit.value.amount == 1000
        assert limit.value.currency == "USD"

    def test_init_negative_limit(self):
        """Test creating a Limit with negative value should raise error."""
        money = Money(-100, "USD")

        with pytest.raises(InvalidLimitValueError) as exc_info:
            Limit(money)

        assert "Limit cannot be negative" in str(exc_info.value)

    @pytest.mark.parametrize(
        "limit1, limit2, should_be_equal",
        [
            pytest.param(
                Limit(Money(1000, "USD")),
                Limit(Money(1000, "USD")),
                True,
                id="same_limit",
            ),
            pytest.param(
                Limit(Money(1000, "USD")),
                Limit(Money(2000, "USD")),
                False,
                id="different_amounts",
            ),
            pytest.param(
                Limit(Money(1000, "USD")),
                Limit(Money(1000, "EUR")),
                False,
                id="different_currencies",
            ),
            pytest.param(
                Limit(Money(1000, "USD")),
                "not a limit object",
                False,
                id="different_types",
            ),
        ],
    )
    def test_equality(self, limit1, limit2, should_be_equal):
        """Test that Limit objects with same value are equal."""
        if should_be_equal:
            assert limit1 == limit2
        else:
            assert limit1 != limit2

    def test_string_representation(self):
        """Test string representation of Limit."""
        limit = Limit(Money(1234, "USD"))
        assert str(limit) == "Limit: 12.34 USD"

    @pytest.mark.parametrize(
        "limit_amount, spending_amount, is_exceeded",
        [
            pytest.param(1000, 500, False, id="not_exceeded"),
            pytest.param(1000, 1000, False, id="exactly_at_limit"),
            pytest.param(1000, 1001, True, id="exceeded"),
            pytest.param(0, -500, False, id="zero_limit"),
        ],
    )
    def test_is_exceeded(self, limit_amount, spending_amount, is_exceeded):
        """Test is_exceeded method."""
        limit = Limit(Money(limit_amount, "USD"))
        spending = Money(spending_amount, "USD")

        assert limit.is_exceeded(spending) == is_exceeded

    def test_is_exceeded_with_invalid_spending(self):
        """Test is_exceeded with invalid spending type."""
        limit = Limit(Money(1000, "USD"))

        # Using monkeypatch instead of passing wrong type directly to avoid type checking errors
        with pytest.raises(AttributeError):
            # We use a workaround to test runtime behavior without triggering static type errors
            # pylint: disable=no-member
            invalid_input: Any = "not a money object"
            limit.is_exceeded(invalid_input)  # type: ignore

    def test_is_exceeded_with_different_currency(self):
        """Test is_exceeded with different currency."""
        limit = Limit(Money(1000, "USD"))
        spending = Money(500, "EUR")

        with pytest.raises(InvalidLimitValueError):
            limit.is_exceeded(spending)

    @pytest.mark.parametrize(
        "limit_amount, spending_amount, expected_remaining",
        [
            pytest.param(1000, 400, 600, id="some_spending"),
            pytest.param(1000, 0, 1000, id="no_spending"),
            pytest.param(1000, 1000, 0, id="at_limit"),
            pytest.param(1000, 1200, 0, id="exceeds_limit"),
            pytest.param(1000, -200, 1200, id="negative_spending"),
        ],
    )
    def test_remaining_amount(self, limit_amount, spending_amount, expected_remaining):
        """Test remaining_amount method."""
        limit = Limit(Money(limit_amount, "USD"))
        spending = Money(spending_amount, "USD")

        remaining = limit.remaining_amount(spending)
        assert remaining.amount == expected_remaining
        assert remaining.currency == "USD"

    def test_remaining_amount_with_invalid_spending(self):
        """Test remaining_amount with invalid spending type."""
        limit = Limit(Money(1000, "USD"))

        with pytest.raises(AttributeError):
            # We use a workaround to test runtime behavior without triggering static type errors
            # pylint: disable=no-member
            invalid_input: Any = "not a money object"
            limit.remaining_amount(invalid_input)  # type: ignore

    def test_remaining_amount_with_different_currency(self):
        """Test remaining_amount with different currency."""
        limit = Limit(Money(1000, "USD"))
        spending = Money(500, "EUR")

        with pytest.raises(CurrencyMismatchError):
            limit.remaining_amount(spending)

    def test_immutability(self):
        """Test that Limit objects are immutable."""
        limit = Limit(Money(1000, "USD"))

        # Using type: ignore to test runtime behavior without triggering static type errors
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            limit.value = Money(2000, "USD")  # type: ignore
