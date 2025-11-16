from typing import Protocol


class TokenRepository(Protocol):
    async def save_token(self, token: str) -> None:
        pass
