from dependency_injector import containers, providers

from .persistence_container import PersistenceContainer
from .publisher_container import PublisherContainer


class AppContainer(containers.DeclarativeContainer):
    """Dependency injection container."""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "adapters.inbound.api",
        ],
        modules=[],
    )

    # Configuration
    config = providers.Configuration()

    # Persistence
    persistence_container: providers.Singleton[PersistenceContainer] = (
        providers.Singleton(PersistenceContainer)
    )

    # Publishers
    publisher_container: providers.Singleton[PublisherContainer] = providers.Singleton(
        PublisherContainer
    )
