import uuid
from dataclasses import dataclass, field

from domain.value_objects import Money


@dataclass
class CategoryStatisticsRecord:
    """Statistics specific to a single category within a budget."""

    category_id: uuid.UUID
    current_balance: Money
    daily_available_amount: Money
    daily_average: Money
    used_limit: Money
    # Add default ID if needed, assuming it's generated here
    id: uuid.UUID = field(default_factory=uuid.uuid4)
