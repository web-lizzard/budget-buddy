import logging
import sys

from configuration import Environment, get_configuration


def setup_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger instance with the specified name.

    Args:
        name: The name of the logger

    Returns:
        logging.Logger: Configured logger instance
    """
    config = get_configuration()

    log_level = (
        logging.INFO
        if config.environment == Environment.DEVELOPMENT
        else logging.WARNING
    )

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add formatter to handler
    console_handler.setFormatter(formatter)

    # Add handler to logger if it doesn't have any handlers
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: The name of the logger

    Returns:
        logging.Logger: Logger instance
    """
    return setup_logger(name)
