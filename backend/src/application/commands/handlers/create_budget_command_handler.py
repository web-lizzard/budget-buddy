from domain.events import BudgetCreated
from domain.events.domain_event import DomainEvent
from domain.factories import BudgetFactory
from domain.factories.budget_factory import CategoryInput
from domain.ports import BudgetRepository
from domain.value_objects import CategoryName, Limit, Money

from application.commands import CategoryData, CreateBudgetCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork


class CreateBudgetCommandHandler(CommandHandler[CreateBudgetCommand]):
    """Handler for the CreateBudgetCommand."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        budget_factory: BudgetFactory,
        unit_of_work: UnitOfWork,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            budget_repository: Repository for persisting budgets
            budget_factory: Factory for creating Budget aggregates
            unit_of_work: UnitOfWork for transaction management and event publishing
        """
        super().__init__(unit_of_work)
        self._budget_repository = budget_repository
        self._budget_factory = budget_factory

    async def _handle(self, command: CreateBudgetCommand) -> DomainEvent:
        """
        Handle the CreateBudgetCommand by creating a new budget.

        Args:
            command: The command to handle

        Returns:
            BudgetCreated domain event
        """
        # Create strategy input based on strategy type
        category_inputs = [
            self._get_category_input(category, command.currency)
            for category in command.categories
        ]

        total_limit = Limit(self._get_money(command.total_limit, command.currency))

        budget = await self._budget_factory.create_budget(
            user_id=command.user_id,
            total_limit=total_limit,
            budget_strategy_input=command.strategy_input,
            start_date=command.start_date,
            categories=category_inputs,
        )

        await self._budget_repository.save(budget=budget, version=0)

        return BudgetCreated(
            budget_id=str(budget.id),
            user_id=str(budget.user_id),
            total_limit=total_limit.value.amount,
            start_date=budget.start_date,
            strategy=str(command.strategy_input.strategy_type),
        )

    def _get_category_input(
        self, category_dto: CategoryData, currency: str
    ) -> CategoryInput:
        """
        Create CategoryInput from DTO.

        Args:
            category_dto: Category DTO from command
            currency: Currency to use for limit

        Returns:
            CategoryInput for budget factory
        """
        category_input = CategoryInput(
            name=CategoryName(category_dto.name),
            limit=Limit(self._get_money(category_dto.limit, currency)),
        )
        return category_input

    def _get_money(self, amount: float, currency: str):
        """
        Create Money value object.

        Args:
            amount: Amount in smallest currency units
            currency: Currency code

        Returns:
            Money value object
        """
        return Money.mint(amount, currency)
