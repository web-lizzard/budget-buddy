from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """Abstract base class for a clock provider."""

    @abstractmethod
    def now(self) -> datetime:
        """Returns the current timezone-aware datetime."""
        raise NotImplementedError
