from application.commands import CreateTransactionCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork
from domain.events.domain_event import DomainEvent
from domain.events.transaction import TransactionAdded
from domain.factories.transaction_factory import (
    TransactionCreateParameters,
    TransactionFactory,
)
from domain.ports.budget_repository import BudgetRepository
from domain.ports.clock import Clock
from domain.ports.transaction_repository import TransactionRepository
from domain.value_objects import TransactionType


class CreateTransactionCommandHandler(CommandHandler[CreateTransactionCommand]):
    """Handler for the CreateTransactionCommand."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        transaction_repository: TransactionRepository,
        transaction_factory: TransactionFactory,
        unit_of_work: UnitOfWork,
        clock: Clock,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            budget_repository: Repository for budget operations
            transaction_repository: Repository for transaction operations
            transaction_factory: Factory for creating transactions
            unit_of_work: UnitOfWork for transaction management and event publishing
            clock: Clock for getting current time
        """
        super().__init__(unit_of_work)
        self._budget_repository = budget_repository
        self._transaction_repository = transaction_repository
        self._transaction_factory = transaction_factory
        self._clock = clock

    async def _handle(self, command: CreateTransactionCommand) -> DomainEvent:
        """
        Handle the CreateTransactionCommand by creating a new transaction.

        Args:
            command: The command to handle

        Returns:
            TransactionAdded domain event
        """
        # Fetch the budget first to get the currency
        _, budget = await self._budget_repository.find_by(
            command.budget_id, command.user_id
        )

        # Get the category from the budget
        category = budget.get_category_by(command.category_id)

        # Prepare parameters for the factory
        create_params = TransactionCreateParameters(
            budget=budget,
            category=category,
            amount=command.amount,
            transaction_type=TransactionType(command.transaction_type),
            occurred_date=command.occurred_date or self._clock.now(),
            description=command.description,
        )

        # Create transaction using the factory and parameters
        transaction = await self._transaction_factory.create(params=create_params)

        # Save transaction to repository
        await self._transaction_repository.save(transaction)

        # Return event
        return TransactionAdded(
            transaction_id=str(transaction.id),
            category_id=str(transaction.category_id),
            amount=transaction.amount.amount,
            type=str(transaction.transaction_type),
            date=transaction.occurred_date,
            budget_id=str(command.budget_id),
            user_id=str(command.user_id),
            occurred_on=self._clock.now(),
        )
