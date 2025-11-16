from dataclasses import dataclass

from auth.domain.exceptions.invalid_email import InvalidEmailError


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not self.value:
            raise InvalidEmailError("Email cannot be empty")
        if "@" not in self.value:
            raise InvalidEmailError("Invalid email format")
        if "." not in self.value:
            raise InvalidEmailError("Invalid email format")
        if self.value.count("@") > 1:
            raise InvalidEmailError("Invalid email format")
