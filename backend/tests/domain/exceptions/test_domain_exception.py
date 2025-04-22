from domain.exceptions import DomainError


class TestDomainError:
    def test_initialization(self):
        """Test if DomainError is initialized correctly."""
        error = DomainError("This is an error message")
        assert error.message == "This is an error message"
        assert error.status == "domain"
        assert str(error) == "This is an error message"

    def test_status_derivation(self):
        """Test status derivation from class name."""

        class CustomDomainError(DomainError):
            pass

        error = CustomDomainError("Custom error")
        assert error.status == "custom_domain"

    def test_status_derivation_with_error_suffix(self):
        """Test status derivation with Error suffix in class name."""

        class BudgetNotFoundError(DomainError):
            pass

        error = BudgetNotFoundError("Budget not found")
        assert error.status == "budget_not_found"

    def test_multi_word_class_name(self):
        """Test status derivation with multiple words in class name."""

        class UserAuthenticationFailedError(DomainError):
            pass

        error = UserAuthenticationFailedError("Authentication failed")
        assert error.status == "user_authentication_failed"
