from domain.events.category import CategoryAdded
from domain.ports.budget_repository import BudgetRepository
from domain.ports.domain_publisher import DomainPublisher
from domain.value_objects import CategoryName, Limit, Money

from application.commands import AddCategoryCommand


class AddCategoryCommandHandler:
    """Handler for the AddCategoryCommand."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        domain_publisher: DomainPublisher,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            budget_repository: Repository for budget operations
            domain_publisher: Publisher for domain events
        """
        self._budget_repository = budget_repository
        self._domain_publisher = domain_publisher

    async def handle(self, command: AddCategoryCommand) -> None:
        """
        Handle the AddCategoryCommand by adding a new category to an existing budget.

        Args:
            command: The command to handle
        """
        version, budget = await self._budget_repository.find_by(
            budget_id=command.budget_id, user_id=command.user_id
        )

        category_name = CategoryName(command.name)
        category_limit = Limit(Money.mint(command.limit, command.currency))

        category = budget.add_category(name=category_name, limit=category_limit)

        await self._budget_repository.save(budget=budget, version=version)

        await self._domain_publisher.publish(
            CategoryAdded(
                category_id=str(category.id),
                budget_id=str(budget.id),
                name=category.name.value,
                limit=category_limit.value.amount,
            )
        )
