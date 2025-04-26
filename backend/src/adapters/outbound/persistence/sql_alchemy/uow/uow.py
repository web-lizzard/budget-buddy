from application.ports.uow import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
