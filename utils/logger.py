"""
This module provides logging functionality for the transformation engine.

It contains utilities for setting up and configuring loggers with appropriate 
handlers and formatters to ensure consistent logging across the application.
"""

import logging


def setup_logger(name="transformation_engine", log_level=logging.INFO):
    """
    Setup and configure a logger with the given name and log level.

    Args:
        name (str): The name of the logger.
        log_level (int): The logging level (default: logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add formatter to console handler
    console_handler.setFormatter(formatter)

    # Check if handlers already exist to avoid duplicate handlers
    if not logger.handlers:
        # Add console handler to logger
        logger.addHandler(console_handler)

    return logger
