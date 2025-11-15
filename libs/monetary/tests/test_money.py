"""
Tests for the Money and Currency classes in the monetary module.
Covers arithmetic operations and checks for float precision errors common in financial code.
"""

from decimal import Decimal

import pytest

from monetary.money import Currency, Money


def test_money_add():
    """Test addition of Money objects with the same currency."""
    assert Money(100, Currency.USD) + Money(200, Currency.USD) == Money(300, Currency.USD)


def test_money_sub():
    """Test subtraction of Money objects with the same currency."""
    assert Money(100, Currency.USD) - Money(200, Currency.USD) == Money(-100, Currency.USD)


def test_money_mul():
    """Test multiplication of Money by an integer."""
    assert Money(100, Currency.USD) * 2 == Money(200, Currency.USD)


def test_money_div():
    """Test integer division of Money by an integer."""
    assert Money(100, Currency.USD) / 2 == Money(50, Currency.USD)


def test_money_eq():
    """Test equality and inequality of Money objects."""
    assert Money(100, Currency.USD) == Money(100, Currency.USD)
    assert Money(100, Currency.USD) != Money(200, Currency.USD)


def test_money_lt():
    """Test the less-than comparison between Money objects."""
    assert Money(100, Currency.USD) < Money(200, Currency.USD)
    assert not Money(100, Currency.USD) < Money(100, Currency.USD)
    assert not Money(200, Currency.USD) < Money(100, Currency.USD)


def test_money_le():
    """Test the less-than-or-equal comparison between Money objects."""
    assert Money(100, Currency.USD) <= Money(200, Currency.USD)
    assert Money(100, Currency.USD) <= Money(100, Currency.USD)
    assert not Money(200, Currency.USD) <= Money(100, Currency.USD)


def test_float_precision_classic_problem():
    """
    Test the classic float precision problem: 0.1 + 0.2 != 0.3 for floats,
    but should work correctly using Money.mint().
    """
    money1 = Money.mint(0.1, Currency.USD)
    money2 = Money.mint(0.2, Currency.USD)
    expected = Money.mint(0.3, Currency.USD)

    result = money1 + money2
    assert result == expected
    assert result.amount == 30
    assert result.amount_in_main_unit == Decimal("0.3")


def test_float_precision_repeated_addition():
    """
    Test repeated addition of small amounts - detects accumulation of float errors.
    """
    result = Money.mint(0.0, Currency.USD)
    for _ in range(10):
        result = result + Money.mint(0.1, Currency.USD)

    expected = Money.mint(1.0, Currency.USD)
    assert result == expected
    assert result.amount == 100
    assert result.amount_in_main_unit == Decimal("1.0")


def test_float_precision_repeating_decimal():
    """
    Test with a decimal number with an infinite repeating decimal expansion.
    """
    money = Money.mint(0.33, Currency.USD)
    result = money * 3

    assert result.amount == 99
    assert result.amount_in_main_unit == Decimal("0.99")


def test_float_precision_large_number():
    """
    Test with large numbers - detects precision issues with high-value amounts.
    """
    money1 = Money.mint(999999.99, Currency.USD)
    money2 = Money.mint(0.01, Currency.USD)

    result = money1 + money2
    expected = Money.mint(1000000.00, Currency.USD)

    assert result == expected
    assert result.amount == 100000000
    assert result.amount_in_main_unit == Decimal("1000000.00")


def test_float_precision_subtraction():
    """
    Test subtraction - checks for precision errors in reverse operations.
    """
    money1 = Money.mint(1.0, Currency.USD)
    money2 = Money.mint(0.9, Currency.USD)

    result = money1 - money2
    expected = Money.mint(0.1, Currency.USD)

    assert result == expected
    assert result.amount == 10


def test_float_precision_complex_calculation():
    """
    Test complex calculations - detects cumulative float errors in more involved expressions.
    """
    money1 = Money.mint(10.50, Currency.USD)
    money2 = Money.mint(20.25, Currency.USD)
    money3 = Money.mint(5.00, Currency.USD)

    result = (money1 + money2) * 2 - money3
    expected = Money.mint(56.50, Currency.USD)

    assert result == expected
    assert result.amount == 5650


def test_float_precision_cents():
    """
    Test operations on cents - most sensitive to precision errors.
    """
    result = Money.mint(0.0, Currency.USD)
    for _ in range(100):
        result = result + Money.mint(0.01, Currency.USD)

    expected = Money.mint(1.00, Currency.USD)
    assert result == expected
    assert result.amount == 100


def test_float_precision_456_problem():
    """
    Test the infamous 4.56 * 100 = 455.99999... problem.
    This specific float value is notoriously problematic.
    """
    money = Money.mint(4.56, Currency.USD)
    assert money.amount == 456
    assert money.amount_in_main_unit == Decimal("4.56")


def test_very_large_amounts():
    """Test with amounts near int64 limits."""
    large_amount = 92233720368547758.07  # Near max safe value
    money = Money.mint(large_amount, Currency.USD)

    assert money.amount_in_main_unit == Decimal(str(large_amount))


def test_negative_amounts():
    """Test operations with negative amounts (refunds, debt)."""
    money = Money.mint(-10.50, Currency.USD)
    assert money.amount == -1050
    assert money.amount_in_main_unit == Decimal("-10.50")


def test_subtraction_resulting_in_negative():
    """Test subtraction that results in negative amount."""
    money1 = Money.mint(5.0, Currency.USD)
    money2 = Money.mint(10.0, Currency.USD)
    result = money1 - money2

    assert result.amount == -500
    assert result.amount_in_main_unit == Decimal("-5.0")


# Tests for currency validation
def test_add_different_currencies_raises_error():
    """Test that adding money with different currencies raises ValueError."""
    usd_money = Money(100, Currency.USD)
    pln_money = Money(100, Currency.PLN)

    with pytest.raises(ValueError, match="Cannot add money with different currencies"):
        usd_money + pln_money


def test_subtract_different_currencies_raises_error():
    """Test that subtracting money with different currencies raises ValueError."""
    usd_money = Money(100, Currency.USD)
    pln_money = Money(100, Currency.PLN)

    with pytest.raises(ValueError, match="Cannot subtract money with different currencies"):
        usd_money - pln_money


def test_compare_lt_different_currencies_raises_error():
    """Test that < comparison with different currencies raises ValueError."""
    usd_money = Money(100, Currency.USD)
    pln_money = Money(100, Currency.PLN)

    with pytest.raises(ValueError, match="Cannot compare money with different currencies"):
        usd_money < pln_money


def test_compare_le_different_currencies_raises_error():
    """Test that <= comparison with different currencies raises ValueError."""
    usd_money = Money(100, Currency.USD)
    pln_money = Money(100, Currency.PLN)

    with pytest.raises(ValueError, match="Cannot compare money with different currencies"):
        usd_money <= pln_money


def test_compare_gt_different_currencies_raises_error():
    """Test that > comparison with different currencies raises ValueError."""
    usd_money = Money(100, Currency.USD)
    pln_money = Money(100, Currency.PLN)

    with pytest.raises(ValueError, match="Cannot compare money with different currencies"):
        usd_money > pln_money


def test_compare_ge_different_currencies_raises_error():
    """Test that >= comparison with different currencies raises ValueError."""
    usd_money = Money(100, Currency.USD)
    pln_money = Money(100, Currency.PLN)

    with pytest.raises(ValueError, match="Cannot compare money with different currencies"):
        usd_money >= pln_money


# Tests for comparison operators (>, >=)
def test_money_gt():
    """Test the greater-than comparison between Money objects."""
    assert Money(200, Currency.USD) > Money(100, Currency.USD)
    assert not Money(100, Currency.USD) > Money(100, Currency.USD)
    assert not Money(100, Currency.USD) > Money(200, Currency.USD)


def test_money_ge():
    """Test the greater-than-or-equal comparison between Money objects."""
    assert Money(200, Currency.USD) >= Money(100, Currency.USD)
    assert Money(100, Currency.USD) >= Money(100, Currency.USD)
    assert not Money(100, Currency.USD) >= Money(200, Currency.USD)


# Tests for properties
def test_amount_property():
    """Test the amount property returns the value in subunits."""
    money = Money(12345, Currency.USD)
    assert money.amount == 12345


def test_amount_in_main_unit_property():
    """Test the amount_in_main_unit property returns Decimal."""
    money = Money(12345, Currency.USD)
    assert money.amount_in_main_unit == Decimal("123.45")


def test_currency_property():
    """Test the currency property returns the Currency enum."""
    money = Money(100, Currency.USD)
    assert money.currency == Currency.USD

    money_pln = Money(100, Currency.PLN)
    assert money_pln.currency == Currency.PLN


# Tests for __str__ method
def test_str_representation():
    """Test the string representation of Money objects."""
    money_usd = Money(12345, Currency.USD)

    money_pln = Money(50000, Currency.PLN)
    assert str(money_pln) == "500 PLN"
    assert str(money_usd) == "123.45 USD"


# Tests for different currencies (PLN)
def test_pln_currency_operations():
    """Test operations with PLN currency."""
    money1 = Money.mint(100.50, Currency.PLN)
    money2 = Money.mint(50.25, Currency.PLN)

    result = money1 + money2
    assert result.amount == 15075
    assert result.currency == Currency.PLN
    assert result.amount_in_main_unit == Decimal("150.75")


def test_pln_subtraction():
    """Test subtraction with PLN currency."""
    money1 = Money.mint(100.00, Currency.PLN)
    money2 = Money.mint(25.50, Currency.PLN)

    result = money1 - money2
    assert result.amount == 7450
    assert result.currency == Currency.PLN


def test_equality_same_currency_different_amount():
    """Test equality with same currency but different amounts."""
    money1 = Money(100, Currency.USD)
    money2 = Money(200, Currency.USD)

    assert money1 != money2
    assert not (money1 == money2)


def test_equality_different_currency_same_amount():
    """Test equality with different currency but same amount."""
    money_usd = Money(100, Currency.USD)
    money_pln = Money(100, Currency.PLN)

    # Should be not equal even with same amount
    assert money_usd != money_pln
    assert not (money_usd == money_pln)


# Tests for edge cases
def test_zero_amount():
    """Test creating and operating with zero amount."""
    zero_money = Money.mint(0.0, Currency.USD)
    assert zero_money.amount == 0
    assert zero_money.amount_in_main_unit == Decimal("0.0")

    # Adding zero
    money = Money.mint(10.0, Currency.USD)
    result = money + zero_money
    assert result == money


def test_multiplication_by_zero():
    """Test multiplication by zero."""
    money = Money.mint(100.0, Currency.USD)
    result = money * 0
    assert result.amount == 0


def test_division_truncates():
    """Test that division truncates (integer division)."""
    money = Money(101, Currency.USD)  # $1.01
    result = money / 2
    assert result.amount == 50  # Should be 50 cents, not 50.5


def test_mint_with_many_decimal_places():
    """Test mint with more than 2 decimal places."""
    # Should truncate to 2 decimal places
    money = Money.mint(10.999, Currency.USD)
    assert money.amount == 1099  # Truncated to 10.99


def test_immutability():
    """Test that Money objects are immutable (frozen dataclass)."""
    money = Money.mint(10.0, Currency.USD)

    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        money._amount_in_subunits = 999


def test_currency_enum_values():
    """Test Currency enum has correct string values."""
    assert Currency.USD.value == "USD"
    assert Currency.PLN.value == "PLN"
