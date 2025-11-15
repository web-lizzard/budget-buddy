import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class Event(BaseModel):
    """Base class for all events."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="The unique identifier of the event"
    )
    occurred_at: datetime = Field(
        default_factory=datetime.now, description="The date and time the event occurred"
    )

    def __str__(self) -> str:
        return f"{self.id} - {self.occurred_at}"
