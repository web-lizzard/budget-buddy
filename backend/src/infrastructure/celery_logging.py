import logging


def configure_celery_logging():
    """Configure Celery logging to silence debug logs."""
    # Set higher log level for Celery's internal components
    logging.getLogger("celery").setLevel(logging.DEBUG)
    logging.getLogger("celery.worker").setLevel(logging.DEBUG)
    logging.getLogger("celery.task").setLevel(logging.DEBUG)
    logging.getLogger("celery.app").setLevel(logging.DEBUG)
    logging.getLogger("celery.utils").setLevel(logging.DEBUG)
