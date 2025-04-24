from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveCategoryCommand:
    """Command for removing a category from a budget."""

    user_id: UUID
    budget_id: UUID
    category_id: UUID
    transfer_policy: str
    target_category_id: UUID | None = (
        None  # Required when transfer_policy is 'transfer'
    )
