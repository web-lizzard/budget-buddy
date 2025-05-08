from typing import Optional

from application.services.security_service import SecurityService  # Added
from application.services.user_service import UserData, UserService
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from infrastructure.container.main_container import MainContainer

from .schemas import (
    NewAccessTokenResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter(
    prefix="auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@inject
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(
        Provide[MainContainer.auth_container.user_service]
    ),
):
    """Registers a new user."""
    # user_service is now injected
    created_user: Optional[UserData] = await user_service.create_user(
        email=user_data.email, password=user_data.password
    )

    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered or invalid data",
        )
    return UserResponse(id=created_user["id"], email=created_user["email"])


@router.post("/login", response_model=TokenResponse)
@inject
async def login_for_access_token(
    form_data: UserLogin,
    user_service: UserService = Depends(
        Provide[MainContainer.auth_container.user_service]
    ),
    security_service: SecurityService = Depends(
        Provide[MainContainer.auth_container.security_service]
    ),
):
    """Logs in a user and returns access and refresh tokens."""
    authenticated_user = await user_service.authenticate_user(
        email=form_data.email, password=form_data.password
    )

    # Use user's ID from authenticated_user for token subject (sub)
    user_identifier_for_token = authenticated_user["id"]

    access_token = security_service.create_access_token(
        data={"sub": user_identifier_for_token}
    )
    refresh_token = security_service.create_refresh_token(
        data={"sub": user_identifier_for_token}
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=NewAccessTokenResponse)
@inject
async def refresh_access_token(
    token_data: RefreshTokenRequest,
    security_service: SecurityService = Depends(
        Provide[MainContainer.auth_container.security_service]
    ),
):
    """Refreshes an access token using a valid refresh token."""
    refresh_token_str = token_data.refresh_token

    # Verify the refresh token and ensure it's a 'refresh' type token
    user_identifier = security_service.verify_token_and_extract_sub(
        token=refresh_token_str, expected_type="refresh"
    )

    if not user_identifier:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a new access token
    new_access_token = security_service.create_access_token(
        data={"sub": user_identifier}
    )

    return NewAccessTokenResponse(access_token=new_access_token)
