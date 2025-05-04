from datetime import datetime, timezone

from domain.ports.clock import Clock


class TimeAwareClock(Clock):
    """Implementation of the Clock port that returns timezone-aware UTC time."""

    def now(self) -> datetime:
        """Returns the current datetime in UTC."""
        return datetime.now(timezone.utc)
