import asyncio
import logging
import uuid

from application.commands import RenewBudgetCommand
from application.commands.handlers import RenewBudgetCommandHandler
from celery import shared_task
from dependency_injector.wiring import Provide, inject
from infrastructure.container.main_container import MainContainer

# Configure logger
logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="budget_renewal_task",
    queue="budget_renewal_queue",
)
@inject
def renew_budget_task(
    self,
    budget_id: str,
    user_id: str,
    handler: RenewBudgetCommandHandler = Provide[
        MainContainer.application_container.provided.get_command_handler.call(
            RenewBudgetCommand
        )
    ],
):
    """
    Celery task for budget renewal.

    Args:
        self: Celery task instance
        budget_id: ID of the budget to renew
        user_id: User ID
        handler: Handler for RenewBudget command (injected by DI)
    """
    logger.info(
        f"Starting budget renewal task for budget {budget_id}, user {user_id} "
        f"(Attempt: {self.request.retries + 1})"
    )

    try:
        # Create command with proper UUID conversion
        command = RenewBudgetCommand(
            budget_id=uuid.UUID(budget_id), user_id=uuid.UUID(user_id)
        )

        # Execute handler in an event loop since it's async
        loop = asyncio.get_event_loop()
        loop.run_until_complete(handler.handle(command))

        logger.info(f"Successfully renewed budget {budget_id}")
        return {"status": "success", "budget_id": budget_id}

    except Exception as exc:
        logger.error(f"Error renewing budget {budget_id}: {exc}", exc_info=True)

        try:
            # Retry with increasing delay
            retry_delay = self.default_retry_delay * (self.request.retries + 1)

            logger.warning(
                f"Retrying task in {retry_delay} seconds "
                f"(Attempt {self.request.retries + 1}/{self.max_retries})"
            )

            self.retry(exc=exc, countdown=retry_delay)

        except self.MaxRetriesExceededError:
            logger.critical(f"Max retries exceeded for budget renewal {budget_id}")
            return {"status": "error", "budget_id": budget_id, "error": str(exc)}
