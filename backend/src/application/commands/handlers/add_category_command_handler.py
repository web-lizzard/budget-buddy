from domain.events.category import CategoryAdded
from domain.events.domain_event import DomainEvent
from domain.ports.budget_repository import BudgetRepository
from domain.value_objects import CategoryName, Limit, Money

from application.commands import AddCategoryCommand
from application.commands.handlers.command_handler import CommandHandler
from application.commands.ports.uow.uow import UnitOfWork


class AddCategoryCommandHandler(CommandHandler[AddCategoryCommand]):
    """Handler for the AddCategoryCommand."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        unit_of_work: UnitOfWork,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            budget_repository: Repository for budget operations
            unit_of_work: UnitOfWork for transaction management and event publishing
        """
        super().__init__(unit_of_work)
        self._budget_repository = budget_repository

    async def _handle(self, command: AddCategoryCommand) -> DomainEvent:
        """
        Handle the AddCategoryCommand by adding a new category to an existing budget.

        Args:
            command: The command to handle

        Returns:
            CategoryAdded domain event
        """
        version, budget = await self._budget_repository.find_by(
            budget_id=command.budget_id, user_id=command.user_id
        )

        category_name = CategoryName(command.name)
        category_limit = Limit(Money.mint(command.limit, command.currency))

        category = budget.add_category(name=category_name, limit=category_limit)

        await self._budget_repository.save(budget=budget, version=version)

        return CategoryAdded(
            category_id=str(category.id),
            budget_id=str(budget.id),
            name=category.name.value,
            limit=category_limit.value.amount,
        )
