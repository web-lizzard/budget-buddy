import asyncio
import functools
from datetime import UTC, datetime, timedelta
from typing import Any, Dict
from unittest.mock import Mock

import jwt
import pytest


def async_step(func):
    """Decorator to make async functions work with pytest-bdd steps."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(func(*args, **kwargs))

    return wrapper


@pytest.fixture
def api_client():
    """Fixture providing API client for testing with async mocks."""

    class MockAPIClient:
        def __init__(self):
            self.base_url = "http://localhost:8000"
            self.last_response = None

            # Create mock methods that raise NotImplementedError
            self._post_mock = Mock(
                side_effect=NotImplementedError("API endpoint not implemented yet")
            )
            self._get_mock = Mock(
                side_effect=NotImplementedError("API endpoint not implemented yet")
            )

        def post(self, endpoint: str, json: Dict[str, Any] = None, headers: Dict[str, str] = None):
            """Mock POST request - raises NotImplementedError until implemented."""
            return self._post_mock(endpoint, json=json, headers=headers)

        def get(self, endpoint: str, headers: Dict[str, str] = None):
            """Mock GET request - raises NotImplementedError until implemented."""
            return self._get_mock(endpoint, headers=headers)

    client = MockAPIClient()
    yield client


@pytest.fixture
def jwt_secret():
    """JWT secret key for testing."""
    return "test-secret-key-change-in-production"


@pytest.fixture
def valid_token(jwt_secret):
    """Generate a valid JWT token for testing."""
    payload = {
        "sub": "user@example.com",
        "user_id": "12345",
        "exp": datetime.now(UTC) + timedelta(hours=24),
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


@pytest.fixture
def expired_token(jwt_secret):
    """Generate an expired JWT token for testing."""
    payload = {
        "sub": "user@example.com",
        "user_id": "12345",
        "exp": datetime.now(UTC) - timedelta(hours=1),
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


@pytest.fixture
def test_user():
    """Test user data."""
    return {"email": "user@example.com", "password": "ValidPass123"}
