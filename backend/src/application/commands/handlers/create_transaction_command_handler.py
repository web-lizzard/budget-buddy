from domain.events.transaction import TransactionAdded
from domain.factories.transaction_factory import TransactionFactory
from domain.ports.budget_repository import BudgetRepository
from domain.ports.domain_publisher import DomainPublisher
from domain.ports.transaction_repository import TransactionRepository
from domain.value_objects import Money

from application.commands import CreateTransactionCommand


class CreateTransactionCommandHandler:
    """Handler for the CreateTransactionCommand."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        transaction_repository: TransactionRepository,
        domain_publisher: DomainPublisher,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            budget_repository: Repository for budget operations
            transaction_repository: Repository for transaction operations
            domain_publisher: Publisher for domain events
        """
        self._budget_repository = budget_repository
        self._transaction_repository = transaction_repository
        self._domain_publisher = domain_publisher

    async def handle(self, command: CreateTransactionCommand) -> None:
        """
        Handle the CreateTransactionCommand by creating a new transaction.

        Args:
            command: The command to handle
        """
        transaction_factory = TransactionFactory(self._budget_repository)

        # Convert amount to Money value object
        amount = Money.mint(command.amount, command.currency)

        # Create transaction
        transaction = await transaction_factory.create_transaction(
            category_id=command.category_id,
            amount=amount,
            transaction_type=command.transaction_type,
            budget_id=command.budget_id,
            user_id=command.user_id,
            occurred_date=command.occurred_date,
            description=command.description,
        )

        # Save transaction to repository
        await self._transaction_repository.save(transaction)

        # Publish event
        await self._domain_publisher.publish(
            TransactionAdded(
                transaction_id=str(transaction.id),
                category_id=str(transaction.category_id),
                amount=amount.amount,
                type=str(transaction.transaction_type),
                date=transaction.occurred_date,
            )
        )
