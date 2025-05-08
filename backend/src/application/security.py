import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

from infrastructure.settings import JWTSettings, get_settings
from jose import JWTError, jwt
from passlib.context import CryptContext

# It's recommended to create the CryptContext instance once and reuse it.
# If you create it inside the functions, it will be slower.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against a hash."""
    # run_in_executor is preferred over run_in_threadpool for CPU-bound tasks
    # like password hashing, as it can utilize a ProcessPoolExecutor.
    # However, for simplicity and consistency with the plan, using run_in_threadpool.
    # Consider changing to loop.run_in_executor(None, pwd_context.verify, plain_password, hashed_password)
    # for potentially better performance in a production environment with multiple CPU cores.
    return await asyncio.to_thread(pwd_context.verify, plain_password, hashed_password)


async def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt."""
    # Similar to verify_password, consider loop.run_in_executor for CPU-bound task.
    return await asyncio.to_thread(pwd_context.hash, password)


settings: JWTSettings = get_settings().jwt


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
    to_encode.update(
        {"exp": expire, "type": "refresh"}
    )  # Add a type claim for refresh token
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_token_and_extract_sub(
    token: str, expected_type: Optional[str] = None
) -> Optional[str]:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        # Verify token type if expected_type is provided
        if expected_type:
            token_type: Optional[str] = payload.get("type")
            if token_type != expected_type:
                return None  # Or raise an exception indicating wrong token type

        sub: Optional[str] = payload.get("sub")
        if sub is None:
            return None
        return sub
    except JWTError:
        return None
