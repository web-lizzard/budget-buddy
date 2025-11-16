from auth.domain.value_objects.email import Email


class User:
    _id: str
    _email: str
    _password: str

    def __init__(self, user_id: str, email: Email, password: str):
        self._id = user_id
        self._email = email.value
        self._password = password

    @property
    def user_id(self) -> str:
        return self._id

    @property
    def password(self) -> str:
        return self._password

    def __str__(self):
        return f"User(id={self._id}, email={self._email})"
