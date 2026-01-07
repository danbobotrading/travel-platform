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
    if settings.is_development or settings.LOG_FORMAT == "text":
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True)
        ])
        
        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stderr,
            level=getattr(logging, settings.LOG_LEVEL)
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
            level=getattr(logging, settings.LOG_LEVEL)
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
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # JSON format for file in production, text in development
        if settings.is_production and settings.LOG_FORMAT == "json":
            formatter = logging.Formatter('%(message)s')
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    logging.getLogger().addHandler(console_handler)
    
    # Set log level for all loggers
    logging.getLogger().setLevel(getattr(logging, settings.LOG_LEVEL))
    
    logger.info(
        "structlog_configured",
        environment=settings.APP_ENV,
        log_level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
        log_file=settings.LOG_FILE
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
