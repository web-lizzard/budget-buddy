# Assuming an application service will handle the business logic
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.application.security import (
    create_access_token,
    create_refresh_token,
    verify_token_and_extract_sub,
)
from backend.src.application.services.user_service import (  # Updated import
    UserData,
    UserService,
)

# Import MainContainer to access database session
from backend.src.infrastructure.container.main_container import MainContainer

# Placeholder for database session dependency
# from infrastructure.db.session import get_db_session # Placeholder


# Updated UserResponse to match UserData more closely for consistency
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    # Consider adding other fields returned by UserService.create_user if any


class UserCreate(BaseModel):
    email: EmailStr
    password: str


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)


# Updated UserService dependency to use a database session
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = MainContainer.database_container.sessionmaker()
    async with session_maker() as session:
        yield session
        # Session is automatically closed by async with


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserService:
    return UserService(session=session)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(
        get_user_service
    ),  # Added UserService dependency
):
    """Registers a new user."""
    created_user: Optional[UserData] = await user_service.create_user(
        email=user_data.email, password=user_data.password
    )

    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered or invalid data",
        )
    # Ensure UserResponse matches the structure of created_user (which is UserData)
    return UserResponse(id=created_user["id"], email=created_user["email"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class NewAccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# For login, we'd typically use OAuth2PasswordRequestForm = Depends()
# but for direct email/password in JSON body, we define a Pydantic model.
class UserLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    form_data: UserLogin,  # Changed from OAuth2PasswordRequestForm to UserLogin for JSON body
    user_service: UserService = Depends(
        get_user_service
    ),  # Added UserService dependency
):
    """Logs in a user and returns access and refresh tokens."""
    authenticated_user: Optional[UserData] = await user_service.authenticate_user(
        email=form_data.email, password=form_data.password
    )

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Use user's ID from authenticated_user for token subject (sub)
    user_identifier_for_token = authenticated_user["id"]

    access_token = create_access_token(data={"sub": user_identifier_for_token})
    refresh_token = create_refresh_token(data={"sub": user_identifier_for_token})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=NewAccessTokenResponse)
async def refresh_access_token(
    token_data: RefreshTokenRequest,
):
    """Refreshes an access token using a valid refresh token."""
    refresh_token_str = token_data.refresh_token

    # Verify the refresh token and ensure it's a 'refresh' type token
    user_identifier = verify_token_and_extract_sub(
        token=refresh_token_str, expected_type="refresh"
    )

    if not user_identifier:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a new access token
    new_access_token = create_access_token(data={"sub": user_identifier})

    return NewAccessTokenResponse(access_token=new_access_token)
