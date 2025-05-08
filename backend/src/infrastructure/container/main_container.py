from dependency_injector import containers, providers

from infrastructure.container.application_container import ApplicationContainer
from infrastructure.container.auth_container import AuthContainer
from infrastructure.container.domain_container import DomainContainer

# Add import for containers
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

    database_container = providers.Container(DatabaseContainer, config=config)
    # Publishers
    publisher_container = providers.Container(PublisherContainer, config=config)

    # Persistence
    persistence_container = providers.Container(
        PersistenceContainer,
        publisher_container=publisher_container,
        database_container=database_container,
    )

    domain_container = providers.Container(
        DomainContainer, persistence_container=persistence_container
    )

    application_container = providers.Container(
        ApplicationContainer,
        persistence_container=persistence_container,
        domain_container=domain_container,
    )

    auth_container = providers.Container(
        AuthContainer,
        config=config,
        persistence_container=persistence_container,
        database_container=database_container,
    )
