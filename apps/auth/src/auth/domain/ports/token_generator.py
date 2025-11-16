from typing import Protocol


class TokenGenerator(Protocol):
    async def generate_access_token(self, user_id: str) -> str:
        pass
