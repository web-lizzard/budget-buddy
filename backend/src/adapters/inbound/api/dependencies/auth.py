from typing import Optional
from uuid import UUID

from application.services import SecurityService
from dependency_injector.wiring import inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from infrastructure.container.main_container import MainContainer

# Hardcoding tokenUrl as per user feedback to not alter settings.py without request.
TOKEN_URL = "/api/v1/auth/login"  # Defined once

reusable_oauth2_mandatory = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)
reusable_oauth2_optional = OAuth2PasswordBearer(tokenUrl=TOKEN_URL, auto_error=False)


@inject
async def get_current_user_id(
    token: str = Depends(reusable_oauth2_mandatory),
    auth_service: SecurityService = Depends(
        MainContainer.auth_container.security_service
    ),
) -> UUID:
    """Dependency to get current user ID from a mandatory JWT access token."""

    user_id = auth_service.verify_token_and_extract_sub(
        token=token, expected_type="access"
    )

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UUID(user_id)


async def get_current_user_id_optional(
    token: Optional[str] = Depends(reusable_oauth2_optional),
    auth_service: SecurityService = Depends(
        MainContainer.auth_container.security_service
    ),
) -> UUID | None:
    """Dependency to get current user ID from an optional JWT access token."""
    if not token:
        return None

    user_id = auth_service.verify_token_and_extract_sub(
        token=token, expected_type="access"
    )

    # If token was provided but is invalid (or not an access token), user_id will be None.
    # This function should return None in such cases for an optional dependency.
    return UUID(user_id)
