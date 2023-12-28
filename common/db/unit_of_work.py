import abc
from common.db import repository, session


class UnitOfWork(abc.ABC):
    repository: repository.Repository

    def __exit__(self, *args):
        self.rollback()

    def __enter__(self):
        return self

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError()


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory=session.get_session) -> None:
        self.session_factory = session_factory

    def __enter__(self, model):
        self.session = self.session_factory()
        self.repository = repository.SQLRepository(self.session, model)

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
