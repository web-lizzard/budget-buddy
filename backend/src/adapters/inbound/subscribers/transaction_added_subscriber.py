import logging
import uuid

import aio_pika
from application.commands import CalculateStatisticsCommand
from application.commands.handlers.calculate_statistics_command_handler import (
    CalculateStatisticsCommandHandler,
)
from dependency_injector.wiring import Provide, inject
from domain.events.transaction import TransactionAdded
from infrastructure.container.main_container import MainContainer
from pydantic import ValidationError

logger = logging.getLogger(__name__)


@inject
async def on_transaction_added_message(
    message: aio_pika.IncomingMessage,
    handler: CalculateStatisticsCommandHandler = Provide[
        MainContainer.application_container.provided.get_command_handler.call(
            CalculateStatisticsCommand
        )
    ],
) -> None:
    """
    Handler for TransactionAdded messages.

    Args:
        message: The received message from RabbitMQ
        handler: Handler for CalculateStatistics command
    """
    async with message.process(requeue=False, ignore_processed=True):
        try:
            logger.info(f"Received message: {message.body.decode()[:100]}...")
            event = TransactionAdded.model_validate_json(message.body)
            logger.debug(f"Deserialized event: {event}")

            command = CalculateStatisticsCommand(
                budget_id=uuid.UUID(event.budget_id),
                user_id=uuid.UUID(event.user_id),
            )

            await handler.handle(command)
            logger.info(
                f"Successfully processed TransactionAdded event for budget {event.budget_id}"
            )

        except ValidationError as e:
            logger.error(f"Failed to deserialize event: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error processing TransactionAdded event: {e}", exc_info=True)
            try:
                await message.nack(requeue=True)
                logger.warning("Message NACKed and requeued due to processing error.")
            except Exception as ack_err:
                logger.error(f"Could not NACK message: {ack_err}")


def register_transaction_added_subscriber(
    channel: aio_pika.abc.AbstractChannel, exchange: aio_pika.abc.AbstractExchange
):
    """
    Registers the subscriber for TransactionAdded events.

    Args:
        channel: RabbitMQ channel
        exchange: RabbitMQ exchange
    """

    async def setup_subscriber():
        # Queue declaration for statistics
        queue_name = "statistics_queue"
        queue = await channel.declare_queue(queue_name, durable=True)

        # Binding for TransactionAdded event
        routing_key = TransactionAdded.__name__
        await queue.bind(exchange, routing_key=routing_key)

        logger.info(f"Waiting for {routing_key} messages on queue '{queue_name}'")

        # Register callback
        await queue.consume(on_transaction_added_message)

        logger.info(
            f"Registered subscriber for {routing_key} events on queue {queue_name}"
        )

    return setup_subscriber
