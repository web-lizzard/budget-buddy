from dependency_injector import containers, providers

from infrastructure.container.domain_container import DomainContainer

from .persistence_container import PersistenceContainer
from .publisher_container import PublisherContainer


class AppContainer(containers.DeclarativeContainer):
    """Dependency injection container."""

    # Configuration
    config = providers.Configuration()

    # Domain
    domain_container = providers.Container(DomainContainer)

    # Publishers
    publisher_container = providers.Container(PublisherContainer)

    # Persistence
    persistence_container = providers.Container(
        PersistenceContainer,
        publisher_container=publisher_container,
    )
