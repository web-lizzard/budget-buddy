from datetime import datetime

from domain.ports.clock import Clock


class FixedClock(Clock):
    def __init__(self, fixed_time: datetime | None = None):
        self.fixed_time = fixed_time or datetime(2023, 1, 1, 12, 0, 0)

    def now(self) -> datetime:
        return self.fixed_time
