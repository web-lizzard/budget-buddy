from abc import ABC
from datetime import datetime


class DomainEvent(ABC):
    def __init__(self):
        self._occurred_on = datetime.now()

    @property
    def occurred_on(self) -> datetime:
        return self._occurred_on
