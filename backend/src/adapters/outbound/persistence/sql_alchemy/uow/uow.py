from application.ports.uow import UnitOfWork
from domain.ports.domain_publisher import DomainPublisher
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession, event_publisher: DomainPublisher):
        super().__init__(event_publisher)
        self.session = session

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
