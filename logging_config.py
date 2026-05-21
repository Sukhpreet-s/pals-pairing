"""Project-wide logging configuration."""

import logging
import logging.handlers
from pathlib import Path


class ExtrasFormatter(logging.Formatter):
    """
    Custom formatter that handles extra fields passed to logger calls.
    
    Specifically handles fields used in extraction_pipeline/pipeline.py:process_record:
    - prompt_type: string identifier for the prompt type
    - length: integer length of content or text
    - content: string content preview (truncated)
    - keys: list of JSON keys
    - fields: list of field names
    """
    
    # Fields that we explicitly support from logger.debug/info/error extra= parameter
    SUPPORTED_FIELDS = {"prompt_type", "length", "content", "keys", "fields"}

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record with support for extra fields.

        @param record - LogRecord instance to format
        @returns Formatted log message with extras
        """
        # Get the base formatted message
        msg = super().format(record)

        # Extract and format only supported extra fields
        extras = {k: v for k, v in record.__dict__.items() if k in self.SUPPORTED_FIELDS}
        
        if extras:
            formatted_extras = ", ".join(
                f"{k}={self._format_value(v)}" for k, v in sorted(extras.items())
            )
            msg = f"{msg} [{formatted_extras}]"
        
        return msg

    @staticmethod
    def _format_value(value) -> str:
        """
        Format a single extra field value based on its type.

        @param value - The value to format
        @returns String representation of the value
        """
        if isinstance(value, str):
            # Escape special characters in strings
            return f'"{value}"'
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif isinstance(value, (list, tuple)):
            # Format lists with reasonable length limits
            items = [ExtrasFormatter._format_value(item) for item in value[:20]]
            formatted = ", ".join(items)
            if len(value) > 20:
                formatted += f", ... +{len(value) - 20} more"
            return f"[{formatted}]"
        elif isinstance(value, dict):
            # Format dicts up to 10 items
            items = [f"{k}={ExtrasFormatter._format_value(v)}" for k, v in list(value.items())[:10]]
            formatted = ", ".join(items)
            if len(value) > 10:
                formatted += f", ... +{len(value) - 10} more"
            return f"{{{formatted}}}"
        else:
            # Fallback for other types
            return repr(value)


def configure_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
) -> logging.Logger:
    """
    Configure logging for the entire project.

    Sets up both console and optional file handlers. Production-compatible with
    standardized formatting, rotation, and level control.

    @param log_level - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    @param log_file - Optional path to log file; if provided, enables file handler
    @returns Root logger instance
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if called multiple times
    if root_logger.hasHandlers():
        return root_logger

    # Custom formatter that handles extra fields
    formatter = ExtrasFormatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional, with rotation)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,  # Keep 5 backup files
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Should be called after configure_logging() has been invoked once.

    @param name - Logger name (typically __name__)
    @returns Logger instance
    """
    return logging.getLogger(name)
