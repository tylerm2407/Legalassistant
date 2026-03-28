"""Structured logging setup using structlog.

Provides JSON-formatted structured logging with user_id context binding.
All modules should use get_logger() instead of the standard library logging
or bare print() statements.
"""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structlog with JSON rendering for production use.

    Sets up structlog processors for timestamping, log level injection,
    and JSON rendering. Also configures the standard library root logger
    so that third-party libraries emit structured output.

    Args:
        log_level: The minimum log level to emit. Defaults to "INFO".
                   Accepts standard level names: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer()
            if log_level == "DEBUG"
            else structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a bound structlog logger with the given name.

    Args:
        name: The logger name, typically __name__ of the calling module.

    Returns:
        A BoundLogger instance that supports structured key-value logging
        and context binding via .bind(user_id=...).
    """
    return structlog.get_logger(name)
