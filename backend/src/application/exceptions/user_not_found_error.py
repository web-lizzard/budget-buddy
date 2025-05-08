from domain.exceptions import DomainError


class UserNotFoundError(DomainError):
    """Exception raised when a user is not found."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")
