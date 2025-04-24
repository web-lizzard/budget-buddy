from domain.events import BudgetRenewed
from domain.events.domain_event import DomainEvent
from domain.factories import BudgetFactory
from domain.ports import BudgetRepository
from domain.services.budget_renewal_service import BudgetRenewalService
from domain.strategies.budget_strategy.budget_strategy import BudgetStrategy

from application.commands import RenewBudgetCommand
from application.commands.handlers.command_handler import CommandHandler
from application.commands.ports.uow.uow import UnitOfWork


class RenewBudgetCommandHandler(CommandHandler[RenewBudgetCommand]):
    """Handler for the RenewBudgetCommand."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        unit_of_work: UnitOfWork,
        strategies: list[BudgetStrategy],
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            budget_repository: Repository for accessing budgets
            budget_renewal_service: Service for renewing budgets
            unit_of_work: UnitOfWork for transaction management and event publishing
        """
        super().__init__(unit_of_work)
        self._budget_repository = budget_repository
        self._strategies = strategies

    async def _handle(self, command: RenewBudgetCommand) -> DomainEvent:
        """
        Handle the RenewBudgetCommand by creating a new budget based on an existing one.

        Args:
            command: The command to handle

        Returns:
            BudgetRenewed domain event
        """

        renewal_service = BudgetRenewalService(BudgetFactory(self._strategies))
        # Find the original budget by ID and user ID
        version, old_budget = await self._budget_repository.find_by(
            budget_id=command.budget_id, user_id=command.user_id
        )

        # Renew the budget using the service
        new_budget = await renewal_service.renew_budget(old_budget)

        # Save the new budget
        await self._budget_repository.save(budget=new_budget, version=0)

        # Create and return the event
        return BudgetRenewed(
            budget_id=str(new_budget.id),
            old_budget_id=str(old_budget.id),
            user_id=str(new_budget.user_id),
            start_date=new_budget.start_date,
            end_date=new_budget.end_date,
        )
