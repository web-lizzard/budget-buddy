from dataclasses import dataclass

from auth.application.dto.login import LoginDTO
from auth.domain.exceptions.invalid_credentials import InvalidCredentialsError
from auth.domain.ports.password_hasher import PasswordHasher
from auth.domain.ports.token_factory import TokenFactory
from auth.domain.ports.token_generator import TokenGenerator
from auth.domain.ports.token_repository import TokenRepository
from auth.domain.ports.user_repository import UserRepository
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.password import Password


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str


class LoginUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_generator: TokenGenerator,
        token_repository: TokenRepository,
        token_factory: TokenFactory,
        access_token_expires_in: int = 900,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_generator = token_generator
        self._token_repository = token_repository
        self._token_factory = token_factory
        self._access_token_expires_in = access_token_expires_in

    async def execute(self, command: LoginCommand) -> LoginDTO:
        email = Email(command.email)
        password = Password(command.password)

        user = await self._user_repository.get_user_by_email(email)
        if user is None:
            raise InvalidCredentialsError("Invalid credentials")

        if not await self._password_hasher.verify_password(password, user.password):
            raise InvalidCredentialsError("Invalid credentials")

        access_token = await self._token_generator.generate_access_token(user.user_id)
        opaque_refresh_token, refresh_token = self._token_factory.create_refresh_token(user.user_id)
        await self._token_repository.save_token(refresh_token)

        return LoginDTO(
            access_token=access_token,
            refresh_token=opaque_refresh_token,
            expires_in=self._access_token_expires_in,
        )
