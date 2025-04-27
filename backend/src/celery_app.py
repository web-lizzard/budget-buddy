import os

from celery import Celery
from infrastructure.container.main_container import MainContainer
from infrastructure.settings import get_settings


def get_celery_app() -> Celery:
    """
    Initialize and configure Celery application.

    Returns:
        Configured Celery application instance
    """
    # Get RabbitMQ URL from environment variable or use default
    rabbitmq_url = os.environ.get(
        "BUDGETBUDDY_RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//"
    )

    # Create Celery app
    app = Celery(
        "budget_buddy_tasks",
        broker=rabbitmq_url,
        backend="rpc://",
        include=["adapters.inbound.tasks.budget_tasks"],
    )

    # Configure Celery
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_track_started=True,
        broker_connection_retry_on_startup=True,
        task_routes={
            "adapters.inbound.tasks.budget_tasks.renew_budget_task": {
                "queue": "budget_renewal_task_queue"
            }
        },
    )

    return app


# Initialize container for use in tasks
container = MainContainer()
container.init_resources()
container.config.from_pydantic(get_settings())

# Create the Celery app
app = get_celery_app()


if __name__ == "__main__":
    app.start()
