from application.commands.ports.uow.uow import UnitOfWork
from domain.ports.domain_publisher import DomainPublisher


class InMemoryUnitOfWork(UnitOfWork):
    """
    In-memory implementation of the UnitOfWork pattern.

    This implementation simply tracks commit and rollback status with flags,
    useful for testing or simple applications without persistent storage.
    """

    def __init__(self, event_publisher: DomainPublisher):
        """
        Initialize the in-memory UnitOfWork.

        Args:
            event_publisher: The publisher that will handle domain events
        """
        super().__init__(event_publisher)
        self.is_committed = False
        self.is_rolled_back = False

    async def _commit(self) -> None:
        """
        Mark the transaction as committed.

        This implementation simply sets a flag indicating that commit was called.
        """
        self.is_committed = True

    async def rollback(self) -> None:
        """
        Mark the transaction as rolled back.

        This implementation simply sets a flag indicating that rollback was called.
        """
        self.is_rolled_back = True
