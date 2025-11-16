import hashlib
import secrets
import uuid
from datetime import datetime, timedelta

from auth.domain.entities.token import RefreshToken, TokenStatus
from auth.domain.ports.token_factory import TokenFactory


class RefreshTokenFactory(TokenFactory):
    def __init__(self, refresh_token_expires_in_seconds: int = 86400, token_length: int = 32):
        self._refresh_token_expires_in_seconds = refresh_token_expires_in_seconds
        self._token_length = token_length

    def create_refresh_token(
        self, user_id: str, session_id: str | None = None
    ) -> tuple[str, RefreshToken]:
        raw_token = secrets.token_urlsafe(self._token_length)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token_prefix = raw_token[:8]

        return raw_token, RefreshToken(
            token_id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id or str(uuid.uuid4()),
            token_hash=token_hash,
            token_prefix=token_prefix,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self._refresh_token_expires_in_seconds),
            status=TokenStatus.ACTIVE,
        )
