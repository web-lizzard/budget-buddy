from dataclasses import dataclass

from domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class CategoryAdded(DomainEvent):
    category_id: str
    budget_id: str
    name: str
    limit: int

    def __post_init__(self):
        # Call parent __init__ since dataclass doesn't do it automatically
        super().__init__()
