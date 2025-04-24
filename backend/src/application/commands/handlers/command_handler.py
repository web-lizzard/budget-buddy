from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from domain.events.domain_event import DomainEvent

from application.commands.command import Command
from application.ports.uow import UnitOfWork

T = TypeVar("T", bound=Command)


class CommandHandler(Generic[T], ABC):
    """
    Abstract base class for command handlers in the application.

    Command handlers are responsible for orchestrating the execution of a specific command,
    coordinating domain logic, and managing side effects through the UnitOfWork.
    Each concrete handler should implement the _handle method to process a specific command type.
    """

    def __init__(self, unit_of_work: UnitOfWork):
        """
        Initialize the command handler with a unit of work.

        Args:
            unit_of_work: The UnitOfWork that will manage transactions and event publishing
        """
        self._unit_of_work = unit_of_work

    async def handle(self, command: T) -> None:
        """
        Handle a command by delegating to the specific handler implementation and managing the transaction.

        This method coordinates the execution flow, delegating to the _handle method for
        command-specific processing. It manages the transaction through the UnitOfWork,
        ensuring that events are published only when the transaction is successful,
        and that rollback occurs in case of errors.

        Args:
            command: The command to handle

        Raises:
            Exception: Any exception that occurred during command processing
        """
        try:
            event = await self._handle(command)
            await self._unit_of_work.commit(event)
        except Exception as e:
            await self._unit_of_work.rollback()
            raise e

    @abstractmethod
    async def _handle(self, command: T) -> DomainEvent:
        """
        Command-specific handling logic to be implemented by concrete command handlers.

        This method should implement the business logic for processing a specific command,
        and return a domain event representing the outcome of the command.

        Args:
            command: The command to handle

        Returns:
            A domain event representing the outcome of the command
        """
        pass
