from domain.events import BudgetDeactivated
from domain.events.domain_event import DomainEvent
from domain.ports import BudgetRepository

from application.commands import DeactivateBudgetCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork


class DeactivateBudgetCommandHandler(CommandHandler[DeactivateBudgetCommand]):
    """Handler for the DeactivateBudgetCommand."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        unit_of_work: UnitOfWork,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            budget_repository: Repository for accessing budgets
            unit_of_work: UnitOfWork for transaction management and event publishing
        """
        super().__init__(unit_of_work)
        self._budget_repository = budget_repository

    async def _handle(self, command: DeactivateBudgetCommand) -> DomainEvent:
        """
        Handle the DeactivateBudgetCommand by deactivating a budget.

        Args:
            command: The command to handle

        Returns:
            BudgetDeactivated domain event
        """
        # Find the budget by ID and user ID
        version, budget = await self._budget_repository.find_by(
            budget_id=command.budget_id, user_id=command.user_id
        )

        # Deactivate the budget
        budget.deactivate_budget()

        # Save the updated budget
        await self._budget_repository.save(budget=budget, version=version)

        # Create and return the event
        # Since we just called deactivate_budget(), the deactivation_date must be non-None
        deactivation_date = budget.deactivation_date
        if deactivation_date is None:
            # This should not happen as we just deactivated the budget
            raise ValueError("Budget deactivation date is unexpectedly None")

        return BudgetDeactivated(
            budget_id=str(budget.id),
            deactivation_date=deactivation_date,
        )
