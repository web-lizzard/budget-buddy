import asyncio
import logging
import sys
from typing import Optional

import aio_pika
from adapters.inbound.subscribers.budget_created_subscriber import (
    register_budget_created_subscriber,
)

# Import subscribers
from adapters.inbound.subscribers.transaction_added_subscriber import (
    register_transaction_added_subscriber,
)
from adapters.inbound.subscribers.transaction_updated_subscriber import (
    register_transaction_updated_subscriber,
)
from aio_pika.abc import AbstractRobustConnection
from infrastructure.container.main_container import MainContainer
from infrastructure.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """
    Main subscriber function - initializes DI container, connects to RabbitMQ,
    and sets up all event subscribers.
    """
    # Initialize DI container
    container = MainContainer()
    settings = get_settings()
    container.config.from_pydantic(settings)
    container.init_resources()

    # Get RabbitMQ configuration
    amqp_url = settings.rabbitmq.url
    exchange_name = settings.rabbitmq.exchange_name

    connection: Optional[AbstractRobustConnection] = None

    try:
        # Connect to RabbitMQ
        connection = await aio_pika.connect_robust(amqp_url)
        if connection is None:
            logger.critical("Failed to connect to RabbitMQ")
            return

        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        # Declare exchange
        exchange = await channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )

        # Set up subscribers
        logger.info("Setting up event subscribers...")

        # Transaction added subscriber
        transaction_subscriber = register_transaction_added_subscriber(
            channel, exchange
        )
        await transaction_subscriber()

        # Transaction updated subscriber
        transaction_updated_subscriber = register_transaction_updated_subscriber(
            channel, exchange
        )
        await transaction_updated_subscriber()

        # Budget created subscriber
        budget_subscriber = register_budget_created_subscriber(channel, exchange)
        await budget_subscriber()

        logger.info("All subscribers registered. Waiting for messages...")

        # Wait indefinitely
        await asyncio.Event().wait()

    except Exception as e:
        logger.critical(
            f"Subscriber service failed to start or run: {e}", exc_info=True
        )
    finally:
        if connection and not connection.is_closed:
            await connection.close()
            logger.info("RabbitMQ connection closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Subscriber service stopped.")
