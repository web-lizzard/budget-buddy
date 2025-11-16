import uuid
from dataclasses import dataclass

from auth.domain.entities.user import User
from auth.domain.exceptions.user_already_exists import UserAlreadyExistsError
from auth.domain.ports.password_hasher import PasswordHasher
from auth.domain.ports.user_repository import UserRepository
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.password import Password


@dataclass(frozen=True)
class RegisterCommand:
    email: str
    password: str


class RegisterUseCase:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, command: RegisterCommand) -> None:
        email = Email(command.email)
        password = Password(command.password)

        user = await self._user_repository.get_user_by_email(email)
        if user:
            raise UserAlreadyExistsError("Email address already exists")

        hashed_password = await self._password_hasher.hash_password(password)

        user = User(email=email, password=hashed_password, user_id=str(uuid.uuid4()))
        await self._user_repository.create_user(user)
