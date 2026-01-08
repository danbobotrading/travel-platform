"""
Structured logging configuration for Travel Platform using structlog.
Simplified version.
"""

import sys
import logging
import structlog


def setup_structlog():
    """Configure structlog."""
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(colors=True),
    ]
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        wrapper_class=structlog.stdlib.BoundLogger,
    )
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=logging.INFO
    )
    
    logger = structlog.get_logger()
    logger.info("structlog_configured", environment="development")
    
    return logger


def get_logger(name=None):
    """Get a logger instance."""
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


# Initialize logger
logger = setup_structlog()
