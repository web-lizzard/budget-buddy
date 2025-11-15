from typing import Protocol
from auth.domain.entities.user import User
from auth.domain.value_objects.email import Email

class UserRepository(Protocol):
    async def create_user(self, user: User) -> None:
        pass

    async def get_user_by_email(self, email: Email) -> User | None:
        pass