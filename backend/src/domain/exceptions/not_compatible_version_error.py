from .domain_exception import DomainError


class NotCompatibleVersionError(DomainError):
    """Raised when budget version conflict is detected."""

    def __init__(self, budget_id: str, expected_version: int, actual_version: int):
        super().__init__(
            f"Budget with id {budget_id} has version conflict. "
            f"Expected version {expected_version}, but got {actual_version}"
        )
