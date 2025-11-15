from auth.domain.ports.password_hasher import PasswordHasher
from auth.domain.value_objects.password import Password
import bcrypt

class BcryptPasswordHasher(PasswordHasher):

    async def hash_password(self, password: Password) -> str:
        return bcrypt.hashpw(password.value.encode('utf-8'), bcrypt.gensalt())

    async def verify_password(self, password: Password, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.value.encode('utf-8'), hashed_password)