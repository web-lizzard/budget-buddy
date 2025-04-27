import logging
from typing import Callable, Optional

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractRobustConnection
from domain.events.domain_event import DomainEvent
from domain.ports.domain_publisher import DomainPublisher

logger = logging.getLogger(__name__)


class RabbitMQDomainPublisher(DomainPublisher):
    """Domain Publisher implementation using RabbitMQ."""

    def __init__(self, amqp_url: str, exchange_name: str = "domain_events"):
        self._amqp_url = amqp_url
        self._exchange_name = exchange_name
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self._exchange: Optional[AbstractExchange] = None

    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to RabbitMQ.

        Args:
            event: The domain event to publish
        """
        await self._connect()
        if not self._exchange:
            logger.error("Cannot publish event, RabbitMQ exchange not available.")
            return

        routing_key = event.get_event_name()
        try:
            message_json = event.model_dump_json().encode()
        except Exception as e:
            logger.error(
                "Failed to serialize event %s: %s",
                type(event).__name__,
                e,
                exc_info=True,
            )
            return

        message = aio_pika.Message(
            body=message_json,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        try:
            await self._exchange.publish(message, routing_key=routing_key)
            logger.debug(
                "Published event %s with routing key %s",
                type(event).__name__,
                routing_key,
            )
        except Exception as e:
            logger.error(
                "Failed to publish event %s: %s", type(event).__name__, e, exc_info=True
            )

    async def _connect(self) -> None:
        if self._connection and not self._connection.is_closed:
            return
        try:
            self._connection = await aio_pika.connect_robust(self._amqp_url)
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                self._exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
            )
            logger.info(
                "Successfully connected to RabbitMQ exchange '%s'.", self._exchange_name
            )
        except Exception as e:
            logger.error("Failed to connect to RabbitMQ: %s", e, exc_info=True)
            raise

    def subscribe(
        self, event_type: type[DomainEvent], subscriber: Callable[[DomainEvent], None]
    ) -> None:
        """Subscribe is not supported in RabbitMQDomainPublisher. Use consumers instead.

        Args:
            event_type: The type of domain event to subscribe to
            subscriber: The callable to be invoked when an event is received
        """
        logger.warning(
            "RabbitMQDomainPublisher.subscribe is a no-op. Subscription managed by consumers."
        )

    def unsubscribe(
        self, event_type: type[DomainEvent], subscriber: Callable[[DomainEvent], None]
    ) -> None:
        """Unsubscribe is not supported in RabbitMQDomainPublisher. Use consumers instead.

        Args:
            event_type: The type of domain event to unsubscribe from
            subscriber: The callable to remove from subscribers
        """
        logger.warning(
            "RabbitMQDomainPublisher.unsubscribe is a no-op. Subscription managed by consumers."
        )

    def get_subscribers(
        self, event_type: type[DomainEvent]
    ) -> list[Callable[[DomainEvent], None]]:
        """Get subscribers is not supported in RabbitMQDomainPublisher. Use consumers instead.

        Args:
            event_type: The type of domain event

        Returns:
            An empty list
        """
        logger.warning(
            "RabbitMQDomainPublisher.get_subscribers is a no-op. Subscription managed by consumers."
        )
        return []

    async def close(self):
        """Close the RabbitMQ connection."""
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()
        logger.info("RabbitMQ connection closed.")
