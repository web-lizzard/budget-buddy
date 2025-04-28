import logging
from datetime import timedelta

import aio_pika
from celery_app import app as celery_app
from dependency_injector.wiring import inject
from domain.events.budget import BudgetCreated
from pydantic import ValidationError

logger = logging.getLogger(__name__)


@inject
async def on_budget_created_message(message: aio_pika.IncomingMessage) -> None:
    """
    Handler for BudgetCreated messages that schedules a Celery task for budget renewal.

    Args:
        message: The received message from RabbitMQ
    """
    async with message.process(requeue=False, ignore_processed=True):
        try:
            logger.info(
                f"Received BudgetCreated message: {message.body.decode()[:100]}..."
            )
            event = BudgetCreated.model_validate_json(message.body)
            logger.debug(f"Deserialized BudgetCreated event: {event}")

            # Schedule task for budget renewal using celery_app
            logger.debug(
                f"Scheduling renewal task with args: budget_id={event.budget_id}, user_id={event.user_id}, "
                f"eta={event.end_date - timedelta(days=1)}"
            )

            # Użyj instancji celery_app aby zaplanować zadanie przez Redis
            task = celery_app.send_task(
                "budget_renewal_task",
                kwargs={"budget_id": event.budget_id, "user_id": event.user_id},
                eta=event.end_date - timedelta(days=1),
                queue="budget_renewal_queue",
            )

            logger.info(
                f"Scheduled renewal task (ID: {task.id}) for budget {event.budget_id}"
            )

        except ValidationError as e:
            logger.error(
                f"Failed to deserialize BudgetCreated event: {e}", exc_info=True
            )
        except Exception as e:
            logger.error(f"Error processing BudgetCreated event: {e}", exc_info=True)
            try:
                await message.nack(requeue=True)
                logger.warning("Message NACKed and requeued due to processing error.")
            except Exception as ack_err:
                logger.error(f"Could not NACK message: {ack_err}")


# Function to register the subscriber in the main application
def register_budget_created_subscriber(
    channel: aio_pika.abc.AbstractChannel, exchange: aio_pika.abc.AbstractExchange
):
    """
    Registers the subscriber for BudgetCreated events.

    Args:
        channel: RabbitMQ channel
        exchange: RabbitMQ exchange

    Returns:
        A coroutine function that sets up the subscriber
    """

    async def setup_subscriber():
        # Queue declaration for budget renewal events
        queue_name = "budget_created_events_queue"
        queue = await channel.declare_queue(queue_name, durable=True)

        # Binding for BudgetCreated event
        routing_key = BudgetCreated.__name__
        await queue.bind(exchange, routing_key=routing_key)

        # Register callback
        await queue.consume(on_budget_created_message)

        logger.info(
            f"Registered subscriber for {routing_key} events on queue {queue_name}"
        )

    # Return coroutine for later execution
    return setup_subscriber
