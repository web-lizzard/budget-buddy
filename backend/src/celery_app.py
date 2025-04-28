from celery import Celery
from infrastructure.celery_logging import configure_celery_logging
from infrastructure.container.main_container import MainContainer
from infrastructure.settings import get_settings


def get_celery_app() -> Celery:
    """
    Initialize and configure Celery application.

    Returns:
        Configured Celery application instance
    """
    # Configure Celery logging
    configure_celery_logging()

    # Get Redis URL from environment variable or use default
    settings = get_settings()
    broker_url = settings.redis.celery_broker_url

    print("--------------------------------")
    print(f"Celery broker URL: {broker_url}")
    print("--------------------------------")

    # Create Celery app
    app = Celery(
        "budget_buddy_tasks",
        broker=broker_url,
        backend=broker_url,  # Używamy Redis również jako backend
        include=["adapters.inbound.tasks.budget_tasks"],
    )

    # Configure Celery
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_track_started=True,
        broker_connection_retry_on_startup=True,
        result_expires=3600,  # wyniki zadań wygasają po godzinie
        task_routes={
            "adapters.inbound.tasks.budget_tasks.renew_budget_task": {
                "queue": "budget_renewal_queue"
            }
        },
        broker_transport_options={
            "visibility_timeout": 3600  # 1 godzina (w sekundach)
        },
    )

    print("--------------------------------")
    for task in app.tasks:
        print(task)
    print("--------------------------------")

    return app


# Initialize container for use in tasks
container = MainContainer()
container.config.from_pydantic(get_settings())
container.init_resources()

app = get_celery_app()


if __name__ == "__main__":
    app.start()
