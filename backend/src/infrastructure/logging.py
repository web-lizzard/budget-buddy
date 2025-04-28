import logging
import sys
from typing import Any

from .settings import Settings


def configure_logging(settings: Settings) -> None:
    """Configure logging for the application.

    Args:
        settings: Application settings
    """
    handlers: list[Any] = [
        logging.StreamHandler(sys.stdout),
    ]

    logging.basicConfig(
        level=settings.logger.level,
        format=settings.logger.format,
        handlers=handlers,
    )

    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("celery.worker").setLevel(logging.INFO)
    logging.getLogger("celery.task").setLevel(logging.INFO)
    logging.getLogger("celery.app").setLevel(logging.INFO)
    logging.getLogger("celery.utils").setLevel(logging.INFO)
