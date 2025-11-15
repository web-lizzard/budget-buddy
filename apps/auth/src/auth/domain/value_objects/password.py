from dataclasses import dataclass
from auth.domain.exceptions.weak_password import WeakPasswordError

@dataclass(frozen=True)
class Password:
    value: str

    def __post_init__(self):
        if not self.value:
            raise WeakPasswordError("Password cannot be empty")
        if len(self.value) < 8:
            raise WeakPasswordError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in self.value):
            raise WeakPasswordError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in self.value):
            raise WeakPasswordError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in self.value):
            raise WeakPasswordError("Password must contain at least one digit")