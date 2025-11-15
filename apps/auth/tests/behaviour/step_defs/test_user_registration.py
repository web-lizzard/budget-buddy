"""Step definitions for user registration feature."""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from conftest import async_step

# ------------------------------------------------------
# Importy Twoich komponentów domenowych/adapters
from auth.application.use_cases.register import RegisterCommand, RegisterUseCase
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.password import Password
from auth.adapters.user_repository import InMemoryUserRepository
from auth.adapters.password_hasher import BcryptPasswordHasher
from auth.domain.entities.user import User
import uuid 

# ------------------------------------------------------

# Ładujemy scenariusze z pliku feature
scenarios("../features/user_registration.feature")

# ============================================================================
# Fixtures i event loop
# ============================================================================

@pytest.fixture
def user_repository():
    """Fixture for InMemoryUserRepository."""
    return InMemoryUserRepository()

@pytest.fixture
def password_hasher():
    """Fixture for BcryptPasswordHasher."""
    return BcryptPasswordHasher()

@pytest.fixture
def register_use_case(user_repository, password_hasher):
    """Fixture for RegisterUseCase."""
    return RegisterUseCase(user_repository, password_hasher)

@pytest.fixture
def test_context():
    """Wspólny kontekst do przechowywania danych między krokami."""
    return {}

# ============================================================================
# GIVEN steps
# ============================================================================

@given("the registration system is available")
def registration_system_available(register_use_case):
    assert register_use_case is not None

@given("I am a new user")
def i_am_new_user(test_context):
    test_context.clear()
    test_context["existing_user"] = False

@given(parsers.parse('a user with email "{email}" is already registered'))
@async_step
async def user_already_registered(user_repository, password_hasher, email, test_context):
    password = "SomeStrongP4ss!"
    password_obj = Password(password)
    hashed_password = await password_hasher.hash_password(password_obj)
    user = User(user_id=str(uuid.uuid4()), email=Email(email), password=hashed_password)
    await user_repository.create_user(user)
    test_context["existing_user"] = True

# ============================================================================
# WHEN steps
# ============================================================================

@when(parsers.parse('I register with email "{email}" and password "{password}"'))
@async_step
async def register_with_credentials(email, password, register_use_case, test_context):
    command = RegisterCommand(email=email, password=password)
    try:
        await register_use_case.execute(command)
        test_context["registration_success"] = True
        test_context["registered_email"] = email
        test_context["plain_password"] = password
        test_context["error"] = None
    except Exception as exc:
        test_context["registration_success"] = False
        test_context["error"] = str(exc)

# ============================================================================
# THEN steps
# ============================================================================

@then("the registration should be successful")
def registration_successful(test_context):
    assert test_context.get("registration_success") is True

@then("the registration should fail")
def registration_should_fail(test_context):
    assert test_context.get("registration_success") is False

@then(parsers.parse('I should see an error message "{message}"'))
def see_error_message(test_context, message):
    assert message in str(test_context.get("error") or "")

@then("my account should be active immediately")
@async_step
async def account_active_immediately(user_repository, test_context):
    user = await user_repository.get_user_by_email(Email(test_context.get("registered_email")))
    assert user is not None
    assert getattr(user, "active", True)  # domyślnie True lub pole aktywności

@then("my password should be hashed in the database")
@async_step
async def password_hashed_in_database(user_repository, test_context):
    user = await user_repository.get_user_by_email(Email(test_context.get("registered_email")))
    assert user.password != test_context.get("plain_password")

@then("the plain password should not be stored in the database")
@async_step
async def plain_password_not_stored(user_repository, test_context):
    user = await user_repository.get_user_by_email(Email(test_context.get("registered_email")))
    assert test_context.get("plain_password") not in user.password

@then("the password should be hashed using bcrypt or argon2")
@async_step
async def password_hashed_with_secure_algorithm(user_repository, test_context):
    user = await user_repository.get_user_by_email(Email(test_context.get("registered_email")))
    assert user.password.startswith("$2") or user.password.startswith("$argon2")

@then("the password should contain uppercase letters")
def password_has_uppercase(test_context):
    assert any(c.isupper() for c in test_context.get("plain_password", ""))

@then("the password should contain lowercase letters")
def password_has_lowercase(test_context):
    assert any(c.islower() for c in test_context.get("plain_password", ""))

@then("the password should contain digits")
def password_has_digits(test_context):
    assert any(c.isdigit() for c in test_context.get("plain_password", ""))

@then("the password should be at least 8 characters long")
def password_min_length(test_context):
    assert len(test_context.get("plain_password", "")) >= 8

@then("I should see an error message about missing uppercase letters")
def see_error_about_uppercase(test_context):
    error = str(test_context.get("error") or "")
    assert "uppercase" in error.lower()

@then("I should see an error message about missing lowercase letters")
def see_error_about_lowercase(test_context):
    error = str(test_context.get("error") or "")
    assert "lowercase" in error.lower()

@then("I should see an error message about missing digits")
def see_error_about_digits(test_context):
    error = str(test_context.get("error") or "")
    assert "digit" in error.lower()

@then("I should see an error message about invalid email format")
def see_error_about_email_format(test_context):
    error = str(test_context.get("error") or "")
    assert "email" in error.lower() and "format" in error.lower()
