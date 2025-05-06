import logging
import uuid

import aio_pika
from application.commands.handlers.recalculate_statistics_after_update_command_handler import (
    RecalculateStatisticsAfterUpdateCommandHandler,
)
from application.commands.recalculate_statistics_after_update_command import (
    RecalculateStatisticsAfterUpdateCommand,
)
from dependency_injector.wiring import Provide, inject
from domain.events.transaction.transaction_updated import TransactionUpdated
from infrastructure.container.main_container import MainContainer
from pydantic import ValidationError

logger = logging.getLogger(__name__)


@inject
async def on_transaction_updated_message(
    message: aio_pika.IncomingMessage,
    handler: RecalculateStatisticsAfterUpdateCommandHandler = Provide[
        MainContainer.application_container.provided.get_command_handler.call(
            RecalculateStatisticsAfterUpdateCommand
        )
    ],
) -> None:
    """
    Handler for TransactionUpdated messages.

    Args:
        message: The received message from RabbitMQ
        handler: Handler for RecalculateStatisticsAfterUpdate command
    """
    async with message.process(requeue=False, ignore_processed=True):
        try:
            logger.info(f"Received message: {message.body.decode()[:100]}...")
            event = TransactionUpdated.model_validate_json(message.body)
            logger.debug(f"Deserialized event: {event}")

            command = RecalculateStatisticsAfterUpdateCommand(
                transaction_id=uuid.UUID(event.transaction_id),
                budget_id=uuid.UUID(event.budget_id),
                user_id=uuid.UUID(event.user_id),
                transaction_occurred_date=event.date,
            )

            await handler.handle(command)
            logger.info(
                f"Successfully processed TransactionUpdated event for transaction {event.transaction_id}"
            )

        except ValidationError as e:
            logger.error(f"Failed to deserialize event: {e}", exc_info=True)
        except Exception as e:
            logger.error(
                f"Error processing TransactionUpdated event: {e}", exc_info=True
            )
            try:
                await message.nack(requeue=True)
                logger.warning("Message NACKed and requeued due to processing error.")
            except Exception as ack_err:
                logger.error(f"Could not NACK message: {ack_err}")


def register_transaction_updated_subscriber(
    channel: aio_pika.abc.AbstractChannel, exchange: aio_pika.abc.AbstractExchange
):
    """
    Registers the subscriber for TransactionUpdated events.

    Args:
        channel: RabbitMQ channel
        exchange: RabbitMQ exchange
    """

    async def setup_subscriber():
        # Queue declaration for statistics
        queue_name = "statistics_queue"
        queue = await channel.declare_queue(queue_name, durable=True)

        # Binding for TransactionUpdated event
        routing_key = TransactionUpdated.__name__
        await queue.bind(exchange, routing_key=routing_key)

        logger.info(f"Waiting for {routing_key} messages on queue '{queue_name}'")

        # Register callback
        await queue.consume(on_transaction_updated_message)

        logger.info(
            f"Registered subscriber for {routing_key} events on queue {queue_name}"
        )

    return setup_subscriber
