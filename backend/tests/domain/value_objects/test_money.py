from decimal import Decimal

import pytest
from domain.exceptions import CurrencyMismatchError, InvalidCurrencyError
from domain.value_objects.money import Money


class TestMoney:
    def test_init_valid_money(self):
        """Test creating a valid Money object."""
        money = Money(1000, "USD")
        assert money.amount == 1000
        assert money.currency == "USD"

    def test_init_with_lowercase_currency(self):
        """Test that currency is converted to uppercase during initialization."""
        money = Money(1000, "usd")
        assert money.currency == "USD"

    @pytest.mark.parametrize(
        "amount, currency, error_msg",
        [
            pytest.param(1000, "", "Invalid currency", id="empty_currency"),
            pytest.param(1000, "USDD", "Invalid currency", id="currency_too_long"),
            pytest.param(1000, 123, "Invalid currency", id="non_string_currency"),
        ],
    )
    def test_init_with_invalid_currency(self, amount, currency, error_msg):
        """Test that invalid currency raises an exception."""
        with pytest.raises(InvalidCurrencyError) as exc:
            Money(amount, currency)
        assert error_msg in str(exc.value)

    @pytest.mark.parametrize(
        "amount, currency, expected_str",
        [
            pytest.param(1234, "USD", "12.34 USD", id="positive_amount"),
            pytest.param(-1234, "USD", "-12.34 USD", id="negative_amount"),
            pytest.param(0, "USD", "0.00 USD", id="zero_amount"),
        ],
    )
    def test_string_representation(self, amount, currency, expected_str):
        """Test string representation of Money."""
        money = Money(amount, currency)
        assert str(money) == expected_str

    @pytest.mark.parametrize(
        "money1, money2, should_be_equal",
        [
            pytest.param(Money(1000, "USD"), Money(1000, "USD"), True, id="same_money"),
            pytest.param(
                Money(1000, "USD"), Money(2000, "USD"), False, id="different_amounts"
            ),
            pytest.param(
                Money(1000, "USD"), Money(1000, "EUR"), False, id="different_currencies"
            ),
            pytest.param(
                Money(1000, "USD"), "not a money object", False, id="different_types"
            ),
        ],
    )
    def test_equality(self, money1, money2, should_be_equal):
        """Test that Money objects with same amount and currency are equal."""
        if should_be_equal:
            assert money1 == money2
        else:
            assert money1 != money2

    def test_add(self):
        """Test adding two Money objects."""
        money1 = Money(1000, "USD")
        money2 = Money(500, "USD")

        result = money1.add(money2)

        assert result.amount == 1500
        assert result.currency == "USD"
        assert result == Money(1500, "USD")

        # Original objects are not modified
        assert money1.amount == 1000
        assert money2.amount == 500

    def test_add_with_different_currencies(self):
        """Test that adding Money objects with different currencies raises an exception."""
        money1 = Money(1000, "USD")
        money2 = Money(500, "EUR")

        with pytest.raises(CurrencyMismatchError):
            money1.add(money2)

    def test_subtract(self):
        """Test subtracting two Money objects."""
        money1 = Money(1000, "USD")
        money2 = Money(300, "USD")

        result = money1.subtract(money2)

        assert result.amount == 700
        assert result.currency == "USD"
        assert result == Money(700, "USD")

        # Original objects are not modified
        assert money1.amount == 1000
        assert money2.amount == 300

    def test_subtract_to_negative(self):
        """Test that subtraction can result in negative amounts."""
        money1 = Money(300, "USD")
        money2 = Money(500, "USD")

        result = money1.subtract(money2)

        assert result.amount == -200
        assert result.currency == "USD"

    def test_subtract_with_different_currencies(self):
        """Test that subtracting Money objects with different currencies raises an exception."""
        money1 = Money(1000, "USD")
        money2 = Money(500, "EUR")

        with pytest.raises(CurrencyMismatchError):
            money1.subtract(money2)

    @pytest.mark.parametrize(
        "factor, expected_amount",
        [
            pytest.param(3, 3000, id="integer_factor"),
            pytest.param(1.5, 1500, id="float_factor"),
            pytest.param(Decimal("2.5"), 2500, id="decimal_factor"),
            pytest.param(0, 0, id="zero_factor"),
            pytest.param(-2, -2000, id="negative_factor"),
        ],
    )
    def test_multiply_by(self, factor, expected_amount):
        """Test multiplying Money by a factor."""
        money = Money(1000, "USD")

        result = money.multiply_by(factor)
        assert result.amount == expected_amount
        assert result.currency == "USD"

    @pytest.mark.parametrize(
        "divisor, expected_amount",
        [
            pytest.param(2, 500, id="integer_divisor"),
            pytest.param(4.0, 250, id="float_divisor"),
            pytest.param(Decimal("5"), 200, id="decimal_divisor"),
            pytest.param(-2, -500, id="negative_divisor"),
        ],
    )
    def test_divide_by(self, divisor, expected_amount):
        """Test dividing Money by a divisor."""
        money = Money(1000, "USD")

        result = money.divide_by(divisor)
        assert result.amount == expected_amount
        assert result.currency == "USD"

    def test_divide_by_zero(self):
        """Test dividing by zero raises an exception."""
        money = Money(1000, "USD")

        with pytest.raises(ValueError):
            money.divide_by(0)

    @pytest.mark.parametrize(
        "float_amount, currency, expected_amount",
        [
            pytest.param(12.34, "USD", 1234, id="positive_float"),
            pytest.param(0, "EUR", 0, id="zero_float"),
            pytest.param(-56.78, "GBP", -5678, id="negative_float"),
            pytest.param(123.456, "JPY", 12345, id="float_with_precision"),
        ],
    )
    def test_mint(self, float_amount, currency, expected_amount):
        """Test creating Money from float amount using mint."""
        money = Money.mint(float_amount, currency)
        assert money.amount == expected_amount
        assert money.currency == currency

    def test_immutability(self):
        """Test that Money objects are immutable."""
        money = Money(1000, "USD")

        with pytest.raises(
            Exception
        ):  # dataclasses.FrozenInstanceError but we don't need to import it
            money.amount = 2000

        with pytest.raises(Exception):
            money.currency = "EUR"
