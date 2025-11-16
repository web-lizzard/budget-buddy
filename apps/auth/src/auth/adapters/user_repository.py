from auth.domain.entities.user import User
from auth.domain.ports.user_repository import UserRepository
from auth.domain.value_objects.email import Email


class InMemoryUserRepository(UserRepository):
    def __init__(self, users: list[User] | None = None):
        self._users = users if users is not None else []

    async def create_user(self, user: User) -> None:
        self._users.append(user)

    async def get_user_by_email(self, email: Email) -> User | None:
        return next((user for user in self._users if user._email == email.value), None)
