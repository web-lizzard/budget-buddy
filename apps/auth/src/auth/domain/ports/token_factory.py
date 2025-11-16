from typing import Protocol

from auth.domain.entities.token import RefreshToken


class TokenFactory(Protocol):
    def create_refresh_token(
        self, user_id: str, session_id: str | None = None
    ) -> tuple[str, RefreshToken]:
        pass
