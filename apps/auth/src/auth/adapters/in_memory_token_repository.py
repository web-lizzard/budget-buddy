from auth.domain.ports.token_repository import TokenRepository


class InMemoryTokenRepository(TokenRepository):
    def __init__(self):
        self._tokens = []

    async def save_token(self, token: str) -> None:
        self._tokens.append(token)
