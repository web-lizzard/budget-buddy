import pytest

from domain.exceptions import DomainError


def test_domain_error_base_class():
    """Test if base DomainError class generates correct code."""
    error = DomainError("test message")
    assert error._code == "domain"


class CustomTestError(DomainError):
    """Test error class for simple name."""

    pass


class ComplexNameTestError(DomainError):
    """Test error class for complex name."""

    pass


class VeryLongAndComplexNameTestError(DomainError):
    """Test error class for very long and complex name."""

    pass


@pytest.mark.parametrize(
    "error_class,expected_code",
    [
        (CustomTestError, "custom_test"),
        (ComplexNameTestError, "complex_name_test"),
        (VeryLongAndComplexNameTestError, "very_long_and_complex_name_test"),
    ],
)
def test_error_code_generation(error_class, expected_code):
    """Test if error codes are generated correctly for different class names."""
    error = error_class("test message")
    assert error._code == expected_code


def test_error_message():
    """Test if error message is properly set."""
    message = "This is a test error message"
    error = DomainError(message)
    assert str(error) == message
