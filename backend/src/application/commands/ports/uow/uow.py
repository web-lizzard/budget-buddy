from abc import ABC, abstractmethod

from domain.events import DomainEvent
from domain.ports.domain_publisher import DomainPublisher


class UnitOfWork(ABC):
    """
    Unit of Work pattern implementation for managing transactions and publishing events.

    This is an abstract base class that defines the contract for UnitOfWork implementations.
    It coordinates committing transactions and publishing domain events,
    ensuring that events are only published when the transaction is successful.
    """

    def __init__(self, event_publisher: DomainPublisher):
        """
        Initialize the UnitOfWork with an event publisher.

        Args:
            event_publisher: The publisher that will handle domain events
        """
        self._event_publisher = event_publisher

    async def commit(self, event: DomainEvent) -> None:
        """
        Commit the transaction and publish the associated domain event.

        This method first commits the transaction by calling the implementation-specific
        _commit method, then publishes the event via the event publisher.

        Args:
            event: The domain event to publish after committing
        """
        await self._commit()
        await self._event_publisher.publish(event)

    @abstractmethod
    async def _commit(self) -> None:
        """
        Implementation-specific method to commit the transaction.

        This method must be implemented by concrete UnitOfWork classes.
        """
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """
        Roll back the transaction in case of errors.

        This method must be implemented by concrete UnitOfWork classes.
        It should handle any cleanup and restoration of the previous state.
        """
        pass
