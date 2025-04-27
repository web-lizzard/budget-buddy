from dependency_injector import containers, providers

from infrastructure.container.application_container import ApplicationContainer
from infrastructure.container.domain_container import DomainContainer

# Add import for DatabaseContainer
from .database_container import DatabaseContainer
from .persistence_container import PersistenceContainer
from .publisher_container import PublisherContainer


class MainContainer(containers.DeclarativeContainer):
    """Dependency injection container."""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "adapters.inbound.api",
            "adapters.inbound.subscribers",
            "adapters.inbound.tasks",
        ]
    )
    # Configuration
    config = providers.Configuration()

    # Database
    database_container = providers.Container(DatabaseContainer, config=config)

    # Domain
    domain_container = providers.Container(DomainContainer)

    # Publishers
    publisher_container = providers.Container(PublisherContainer)

    # Persistence
    persistence_container = providers.Container(
        PersistenceContainer,
        publisher_container=publisher_container,
        database_container=database_container,
    )

    application_container = providers.Container(
        ApplicationContainer,
        persistence_container=persistence_container,
        domain_container=domain_container,
    )
