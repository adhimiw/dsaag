"""Logging configuration using loguru."""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

_logger_configured = False


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
) -> None:
    """Configure loguru logger with console and file handlers.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        rotation: Log file rotation size
        retention: Log file retention period
    """
    global _logger_configured

    if _logger_configured:
        return

    # Remove default handler
    logger.remove()

    # Add console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation=rotation,
            retention=retention,
            compression="zip",
        )

    _logger_configured = True


def get_logger(name: Optional[str] = None):
    """Get a logger instance.

    Args:
        name: Optional logger name (usually module name)

    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger

