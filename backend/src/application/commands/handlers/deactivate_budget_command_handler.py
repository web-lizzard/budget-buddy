from domain.events.budget.budget_deactivated import BudgetDeactivated
from domain.ports.budget_repository import BudgetRepository
from domain.ports.clock import Clock
from domain.services.budget_deactivation_service import BudgetDeactivationService

from application.commands import DeactivateBudgetCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork


class DeactivateBudgetCommandHandler(CommandHandler[DeactivateBudgetCommand]):
    """Handler for the DeactivateBudgetCommand."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        budget_deactivation_service: BudgetDeactivationService,
        unit_of_work: UnitOfWork,
        clock: Clock,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            budget_repository: Repository for budget operations
            budget_deactivation_service: Service for deactivating budgets.
            unit_of_work: UnitOfWork for transaction management and event publishing
            clock: Clock for getting current time
        """
        super().__init__(unit_of_work)
        self._budget_deactivation_service = budget_deactivation_service
        self._budget_repository = budget_repository
        self._clock = clock

    async def _handle(self, command: DeactivateBudgetCommand) -> BudgetDeactivated:
        """
        Handle the DeactivateBudgetCommand by deactivating a budget using the service.

        Args:
            command: The command to handle

        Returns:
            BudgetDeactivated domain event
        """

        # Get the budget from the repository
        version, budget = await self._budget_repository.find_by(
            budget_id=command.budget_id, user_id=command.user_id
        )

        # Use the service to deactivate the budget
        deactivation_date = await self._budget_deactivation_service.deactivate(
            budget=budget
        )

        await self._budget_repository.save(budget=budget, version=version)

        # The service always returns a datetime, and the budget's deactivation_date is set if it was None
        return BudgetDeactivated(
            budget_id=str(budget.id),
            deactivation_date=deactivation_date,  # This is always a datetime, not None
            occurred_on=self._clock.now(),
        )
