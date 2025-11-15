from typing import Protocol
from auth.domain.value_objects.password import Password

class PasswordHasher(Protocol):
    async def hash_password(self, password: Password) -> str:
        pass

    async def verify_password(self, password: Password, hashed_password: str) -> bool:
        pass