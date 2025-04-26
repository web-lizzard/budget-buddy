from adapters.inbound.in_memory_domain_publisher import InMemoryDomainPublisher
from dependency_injector import containers, providers
from domain.ports.domain_publisher import DomainPublisher


class PublisherContainer(containers.DeclarativeContainer):
    """Dependency injection container for publishers."""

    domain_publisher: providers.Provider[DomainPublisher] = providers.Singleton(
        InMemoryDomainPublisher
    )
