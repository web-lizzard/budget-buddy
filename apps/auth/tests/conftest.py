from datetime import UTC, datetime, timedelta
from typing import Any, Dict

import httpx
import jwt
import pytest


@pytest.fixture
def api_client():
    """Fixture providing API client for testing."""

    # This should be replaced with your actual API client
    # For example: TestClient from FastAPI or requests.Session
    class MockAPIClient:
        def __init__(self):
            self.base_url = "http://localhost:8000"
            self.client = httpx.Client(base_url=self.base_url)

            self.last_response = None

        def post(self, endpoint: str, json: Dict[str, Any] = None, headers: Dict[str, str] = None):
            # Mock implementation - replace with actual HTTP client
            raise NotImplementedError("API endpoint not implemented yet")

        def get(self, endpoint: str, headers: Dict[str, str] = None):
            # Mock implementation - replace with actual HTTP client
            raise NotImplementedError("API endpoint not implemented yet")

        def __del__(self):
            self.client.close()

    client = MockAPIClient()
    yield client
    del client


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
