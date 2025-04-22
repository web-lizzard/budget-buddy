from .domain_exception import DomainError


class InvalidStrategyParameterError(DomainError):
    """Exception raised when budget strategy parameter is invalid."""

    def __init__(self, parameter_name, parameter_value):
        super().__init__(
            f"Invalid budget strategy parameter '{parameter_name}': {parameter_value}"
        )
