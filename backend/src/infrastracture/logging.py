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

    # Set log level for external libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
