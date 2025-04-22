from domain.exceptions.domain_exception import DomainError


class InvalidStrategyTypeError(DomainError):
    """Exception raised when budget strategy type is invalid."""

    def __init__(self, strategy_type):
        super().__init__(f"Invalid budget strategy type: {strategy_type}")


class InvalidStrategyParameterError(DomainError):
    """Exception raised when budget strategy parameter is invalid."""

    def __init__(self, parameter_name, parameter_value):
        super().__init__(
            f"Invalid budget strategy parameter '{parameter_name}': {parameter_value}"
        )
