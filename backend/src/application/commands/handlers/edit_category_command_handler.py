from uuid import UUID

from domain.events.category.category_edited import CategoryEdited
from domain.ports.budget_repository import BudgetRepository
from domain.ports.clock import Clock
from domain.value_objects.category_name import CategoryName
from domain.value_objects.limit import Limit
from domain.value_objects.money import Money

from application.commands.edit_category_command import EditCategoryCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork


class EditCategoryCommandHandler(CommandHandler[EditCategoryCommand]):
    """
    Command handler for editing an existing category in a budget.

    This handler orchestrates:
    1. Retrieving the budget from the repository
    2. Finding the category within the budget
    3. Updating the category with new name and limit
    4. Saving the updated budget
    5. Returning a CategoryEdited event
    """

    def __init__(
        self,
        budget_repository: BudgetRepository,
        unit_of_work: UnitOfWork,
        clock: Clock,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            budget_repository: Repository for budget operations
            unit_of_work: UnitOfWork for transaction management and event publishing
            clock: Clock for getting current time
        """
        super().__init__(unit_of_work)
        self._budget_repository = budget_repository
        self._clock = clock

    async def _handle(self, command: EditCategoryCommand) -> CategoryEdited:
        """
        Process the EditCategoryCommand.

        Args:
            command: The command to process

        Returns:
            CategoryEdited event with details of the updated category

        Raises:
            BudgetNotFoundError: If the budget is not found or doesn't belong to the user
            CategoryNotFoundError: If the category doesn't exist in the budget
            DuplicateCategoryNameError: If another category with the same name already exists
            CategoryLimitExceedsBudgetError: If the new category limit causes the total to exceed the budget limit
        """
        budget_id = UUID(command.budget_id)
        user_id = UUID(command.user_id)
        category_id = UUID(command.category_id)
        version, budget = await self._budget_repository.find_by(budget_id, user_id)

        updated_category = budget.edit_category(
            category_id,
            self._get_category_name(command),
            self._get_limit(command, budget.currency),
        )

        await self._budget_repository.save(budget, version)

        return CategoryEdited(
            category_id=str(updated_category.id),
            budget_id=str(budget.id),
            name=updated_category.name.value,
            limit=int(updated_category.limit.value.amount),
            occurred_on=self._clock.now(),
        )

    def _get_category_name(self, command: EditCategoryCommand) -> CategoryName | None:
        """Get the category name from the command."""
        return CategoryName(command.name) if command.name else None

    def _get_limit(self, command: EditCategoryCommand, currency: str) -> Limit | None:
        """Get the limit from the command."""
        return Limit(Money.mint(command.limit, currency)) if command.limit else None
