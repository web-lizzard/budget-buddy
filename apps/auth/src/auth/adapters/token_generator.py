import uuid
from datetime import UTC, datetime, timedelta

from authlib.jose import jwt

from auth.domain.ports.token_generator import TokenGenerator


class JWTTokenGenerator(TokenGenerator):
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "RS256",
        access_token_expires_in_seconds: int = 900,
        issuer: str = "auth",
    ):
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._issuer = issuer
        self._access_token_expires_in_seconds = access_token_expires_in_seconds

    async def generate_access_token(self, user_id: str) -> str:
        payload = self._get_payload(user_id)
        token = jwt.encode({"alg": self._algorithm}, payload, self._secret_key)
        return token if isinstance(token, str) else token.decode("utf-8")

    def _get_payload(self, user_id: str) -> dict:
        return {
            "sub": user_id,
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(seconds=self._access_token_expires_in_seconds),
            "iss": self._issuer,
            "jti": str(uuid.uuid4()),
        }
