from dataclasses import dataclass

from domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class CategoryEdited(DomainEvent):
    """
    Domain event emitted when a category is edited.

    Attributes:
        category_id: The ID of the edited category
        budget_id: The ID of the budget containing the category
        name: The new name of the category
        limit: The new limit of the category in smallest currency units
    """

    category_id: str
    budget_id: str
    name: str
    limit: int

    def __post_init__(self):
        # Call parent __init__ since dataclass doesn't do it automatically
        super().__init__()
