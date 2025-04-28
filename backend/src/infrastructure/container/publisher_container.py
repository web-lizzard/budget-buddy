from adapters.outbound.domain_publisher import RabbitMQDomainPublisher
from dependency_injector import containers, providers
from domain.ports.domain_publisher import DomainPublisher


class PublisherContainer(containers.DeclarativeContainer):
    """Dependency injection container for publishers."""

    config = providers.Configuration()

    domain_publisher: providers.Provider[DomainPublisher] = providers.Singleton(
        RabbitMQDomainPublisher,
        amqp_url=providers.Callable(lambda c: c["rabbitmq"]["url"], config),
        exchange_name=providers.Callable(
            lambda c: c["rabbitmq"]["exchange_name"], config
        ),
    )
