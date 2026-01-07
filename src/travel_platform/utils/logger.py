"""
Structured logging configuration for Travel Platform using structlog.

This module provides structured logging with JSON formatting for production
and human-readable formatting for development.
"""

import sys
import logging
import structlog
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.core.config.settings import settings


def setup_structlog() -> structlog.BoundLogger:
    """
    Configure structlog with appropriate processors and formatters.
    
    Returns:
        structlog.BoundLogger: Configured logger instance
    """
    # Get log level from settings or default
    log_level = getattr(settings, 'LOG_LEVEL', 'INFO')
    log_format = getattr(settings, 'LOG_FORMAT', 'text')
    log_file = getattr(settings, 'LOG_FILE', None)
    
    # Common processors for all environments
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Development environment: human-readable format
    if settings.APP_ENV == "development" or log_format == "text":
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True)
        ])
        
        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stderr,
            level=getattr(logging, log_level)
        )
    
    # Production/Staging: JSON format
    else:
        processors.extend([
            structlog.processors.JSONRenderer()
        ])
        
        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stderr,
            level=getattr(logging, log_level)
        )
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        wrapper_class=structlog.stdlib.BoundLogger,
    )
    
    # Get a logger instance
    logger = structlog.get_logger()
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level))
        
        # JSON format for file in production, text in development
        if settings.APP_ENV == "production" and log_format == "json":
            formatter = logging.Formatter('%(message)s')
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, log_level))
    logging.getLogger().addHandler(console_handler)
    
    # Set log level for all loggers
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    logger.info(
        "structlog_configured",
        environment=settings.APP_ENV,
        log_level=log_level,
        log_format=log_format
    )
    
    return logger


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a configured structlog logger instance.
    
    Args:
        name: Logger name. If None, returns the root logger.
    
    Returns:
        structlog.BoundLogger: Logger instance
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


# Initialize logger
logger = setup_structlog()
