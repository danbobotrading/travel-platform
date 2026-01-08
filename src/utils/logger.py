"""
Structured logging configuration for Travel Platform.
Uses structlog for production-ready logging with JSON output.
"""
import sys
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import structlog
from structlog.processors import (
    JSONRenderer,
    TimeStamper,
    add_log_level,
    UnicodeDecoder,
    format_exc_info,
)
from structlog.types import EventDict, Processor
from structlog.stdlib import (
    BoundLogger,
    LoggerFactory,
    add_logger_name,
    filter_by_level,
)
from structlog.contextvars import merge_contextvars

# Import settings from src.core.config
try:
    from src.core.config.settings import settings
except ImportError:
    # Fallback for development
    from dataclasses import dataclass
    
    @dataclass
    class FallbackSettings:
        APP_ENV: str = "development"
        LOG_LEVEL: str = "INFO"
        LOG_FORMAT: str = "console"
    
    settings = FallbackSettings()


class TravelPlatformLogger:
    """Main logger class for Travel Platform."""
    
    _logger: Optional[BoundLogger] = None
    
    @classmethod
    def _get_processors(cls) -> List[Processor]:
        """Get log processors based on environment."""
        processors: List[Processor] = [
            merge_contextvars,
            add_log_level,
            add_logger_name,
            TimeStamper(fmt="iso", utc=True),
            UnicodeDecoder(),
            filter_by_level,
        ]
        
        # Get log format from settings or default to console for development
        log_format = getattr(settings, 'LOG_FORMAT', 'console')
        
        if log_format == "json":
            # JSON format for production
            processors.extend([
                format_exc_info,
                cls._clean_sensitive_data,
                JSONRenderer()
            ])
        else:
            # Pretty console output for development
            try:
                from structlog.dev import ConsoleRenderer
                processors.extend([
                    format_exc_info,
                    cls._clean_sensitive_data,
                    ConsoleRenderer(colors=True)
                ])
            except ImportError:
                # Fallback if ConsoleRenderer not available
                processors.extend([
                    format_exc_info,
                    cls._clean_sensitive_data,
                    structlog.processors.KeyValueRenderer()
                ])
        
        return processors
    
    @staticmethod
    def _clean_sensitive_data(_: Any, __: Any, event_dict: EventDict) -> EventDict:
        """Remove sensitive data from logs."""
        sensitive_keys = [
            'password', 'token', 'secret', 'key', 'authorization',
            'api_key', 'access_token', 'refresh_token', 'credit_card',
            'telegram_bot_token'
        ]
        
        for key in list(event_dict.keys()):
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                event_dict[key] = '[REDACTED]'
        
        return event_dict
    
    @classmethod
    def _configure_logging(cls) -> None:
        """Configure structlog and standard logging."""
        # Get log level from settings or default to INFO
        log_level = getattr(settings, 'LOG_LEVEL', 'INFO').upper()
        log_level_num = getattr(logging, log_level, logging.INFO)
        
        # Configure structlog
        structlog.configure(
            processors=cls._get_processors(),
            wrapper_class=structlog.make_filtering_bound_logger(log_level_num),
            logger_factory=LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        # Configure standard logging for third-party libraries
        logging.basicConfig(
            format="%(message)s",
            level=logging.WARNING,  # Only show warnings for third-party libs
            stream=sys.stdout,
        )
    
    @classmethod
    def get_logger(cls, name: str = "travel_platform") -> BoundLogger:
        """Get a logger instance."""
        if cls._logger is None:
            cls._configure_logging()
        
        return structlog.get_logger(name)
    
    @classmethod
    def bind_context(cls, **kwargs: Any) -> None:
        """Bind context variables to all subsequent log calls."""
        structlog.contextvars.bind_contextvars(**kwargs)
    
    @classmethod
    def unbind_context(cls, *keys: str) -> None:
        """Unbind context variables."""
        structlog.contextvars.unbind_contextvars(*keys)
    
    @classmethod
    def clear_context(cls) -> None:
        """Clear all context variables."""
        structlog.contextvars.clear_contextvars()


# Create module-level logger instance
logger = TravelPlatformLogger.get_logger()

# Convenience functions
def get_logger(name: str = "travel_platform") -> BoundLogger:
    """Get a named logger instance."""
    return TravelPlatformLogger.get_logger(name)

def log_request(request_id: str, method: str, path: str, user_id: Optional[str] = None) -> None:
    """Log HTTP request with context."""
    TravelPlatformLogger.bind_context(
        request_id=request_id,
        method=method,
        path=path,
        user_id=user_id or "anonymous",
        timestamp=datetime.utcnow().isoformat()
    )
    logger.info("request_started")

def log_response(request_id: str, status_code: int, duration_ms: float) -> None:
    """Log HTTP response."""
    logger.info(
        "request_completed",
        request_id=request_id,
        status_code=status_code,
        duration_ms=duration_ms
    )
    TravelPlatformLogger.unbind_context("request_id", "method", "path", "user_id")

def log_error(error_type: str, message: str, exc_info: Optional[Exception] = None, **context: Any) -> None:
    """Log error with context."""
    logger.error(
        error_type,
        error_message=message,
        exc_info=exc_info,
        **context
    )

def log_user_action(user_id: str, action: str, details: Dict[str, Any]) -> None:
    """Log user action for analytics."""
    logger.info(
        "user_action",
        user_id=user_id,
        action=action,
        details=details,
        timestamp=datetime.utcnow().isoformat()
    )
