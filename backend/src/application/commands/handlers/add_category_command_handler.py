from uuid import UUID

from domain.events.category.category_added import CategoryAdded
from domain.ports.budget_repository import BudgetRepository
from domain.value_objects.category_name import CategoryName
from domain.value_objects.limit import Limit
from domain.value_objects.money import Money

from application.commands.add_category_command import AddCategoryCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork


class AddCategoryCommandHandler(CommandHandler[AddCategoryCommand]):
    """
    Command handler for adding a new category to a budget.

    This handler orchestrates:
    1. Retrieving the budget from the repository
    2. Adding a new category to the budget with specified name and limit
    3. Saving the updated budget
    4. Returning a CategoryAdded event
    """

    def __init__(self, budget_repository: BudgetRepository, unit_of_work: UnitOfWork):
        """
        Initialize the AddCategoryCommandHandler with required repositories and unit of work.

        Args:
            budget_repository: Repository for budget aggregate operations
            unit_of_work: Unit of work for managing transactions and event publishing
        """
        super().__init__(unit_of_work)
        self._budget_repository = budget_repository

    async def _handle(self, command: AddCategoryCommand) -> CategoryAdded:
        """
        Process the AddCategoryCommand.

        Args:
            command: The command to process

        Returns:
            CategoryAdded event with details of the newly added category

        Raises:
            BudgetNotFoundError: If the budget is not found or doesn't belong to the user
            MaxCategoriesReachedError: If the budget already has the maximum number of categories
            DuplicateCategoryNameError: If a category with the same name already exists
            CategoryLimitExceedsBudgetError: If the category limit exceeds the available budget limit
        """
        budget_id = UUID(command.budget_id)
        user_id = UUID(command.user_id)
        version, budget = await self._budget_repository.find_by(budget_id, user_id)

        category_name = CategoryName(command.name)
        category_limit = Limit(Money.mint(command.limit, budget.currency))

        category = budget.add_category(category_name, category_limit)

        await self._budget_repository.save(budget, version)

        return CategoryAdded(
            category_id=str(category.id),
            budget_id=str(budget.id),
            name=category.name.value,
            limit=int(category.limit.value.amount),
        )
