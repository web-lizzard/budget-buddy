from abc import ABC
from datetime import datetime


class DomainEvent(ABC):
    @property
    def occurred_on(self) -> datetime:
        return datetime.now()
