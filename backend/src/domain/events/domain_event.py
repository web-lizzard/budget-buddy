import uuid
from datetime import datetime

import pydantic


class DomainEvent(pydantic.BaseModel):
    event_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    occurred_on: datetime
    version: int = 1

    def to_dict(self) -> dict:
        return self.model_dump(mode="json")

    def get_event_name(self) -> str:
        return self.__class__.__name__
