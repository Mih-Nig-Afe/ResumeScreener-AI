"""
Production-grade logging infrastructure for ResumeScreener-AI.

This module provides structured logging with configurable output destinations,
log levels, file rotation, and context-aware formatting. It supports both
console and file output with automatic log rotation to prevent disk space issues.

Example:
    Basic usage with default configuration:
    
    >>> from logging_config import setup_logging, get_logger
    >>> setup_logging()
    >>> logger = get_logger(__name__)
    >>> logger.info("Processing started")
    
    Advanced usage with custom configuration:
    
    >>> from logging_config import setup_logging, LoggingConfiguration
    >>> from pathlib import Path
    >>> config = LoggingConfiguration(
    ...     log_level="DEBUG",
    ...     log_file=Path("logs/app.log"),
    ...     max_file_size=20 * 1024 * 1024,  # 20 MB
    ...     backup_count=10
    ... )
    >>> setup_logging(config)
"""

import logging
import logging.handlers
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class LoggingConfiguration:
    """
    Configuration for the logging system.
    
    This dataclass encapsulates all logging configuration parameters,
    providing sensible defaults for production use while allowing
    full customization for different deployment environments.
    
    Attributes:
        log_level: Minimum log level to capture (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format string for log messages (uses standard logging format specifiers)
        log_file: Optional path to log file. If None, file logging is disabled
        enable_console: Whether to output logs to console (stdout/stderr)
        enable_file: Whether to output logs to file (requires log_file to be set)
        max_file_size: Maximum size of log file in bytes before rotation (default: 10 MB)
        backup_count: Number of rotated log files to keep (default: 5)
    
    Example:
        >>> config = LoggingConfiguration(
        ...     log_level="INFO",
        ...     log_file=Path("logs/resumescreener.log"),
        ...     max_file_size=10 * 1024 * 1024,
        ...     backup_count=5
        ... )
    """
    
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[Path] = None
    enable_console: bool = True
    enable_file: bool = False
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    
    def __post_init__(self) -> None:
        """
        Validate configuration after initialization.
        
        Raises:
            ValueError: If log_level is invalid or configuration is inconsistent
        """
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            raise ValueError(
                f"Invalid log_level '{self.log_level}'. "
                f"Must be one of: {', '.join(valid_levels)}"
            )
        
        # Normalize log level to uppercase
        self.log_level = self.log_level.upper()
        
        # Validate file logging configuration
        if self.enable_file and self.log_file is None:
            raise ValueError(
                "enable_file is True but log_file is not set. "
                "Either set log_file or disable file logging."
            )
        
        # Validate file size and backup count
        if self.max_file_size <= 0:
            raise ValueError(f"max_file_size must be positive, got {self.max_file_size}")
        
        if self.backup_count < 0:
            raise ValueError(f"backup_count must be non-negative, got {self.backup_count}")
        
        # Ensure at least one output destination is enabled
        if not self.enable_console and not self.enable_file:
            raise ValueError(
                "At least one output destination must be enabled "
                "(enable_console or enable_file)"
            )


def setup_logging(config: Optional[LoggingConfiguration] = None) -> None:
    """
    Configure the logging system with the specified configuration.
    
    This function sets up the root logger with handlers for console and/or
    file output, configures log formatting, and enables log rotation for
    file output. It should be called once at application startup.
    
    Args:
        config: Optional LoggingConfiguration object. If None, uses default configuration
                with INFO level and console output only.
    
    Raises:
        ValueError: If configuration is invalid
        OSError: If log file directory cannot be created
    
    Example:
        >>> # Use default configuration
        >>> setup_logging()
        
        >>> # Use custom configuration
        >>> from pathlib import Path
        >>> config = LoggingConfiguration(
        ...     log_level="DEBUG",
        ...     log_file=Path("logs/app.log")
        ... )
        >>> setup_logging(config)
    
    Note:
        This function modifies the root logger configuration. Calling it
        multiple times will add duplicate handlers. To reconfigure logging,
        clear existing handlers first or restart the application.
    """
    # Use default configuration if none provided
    if config is None:
        config = LoggingConfiguration()
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set log level
    log_level = getattr(logging, config.log_level)
    root_logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(config.log_format)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add console handler if enabled
    if config.enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler with rotation if enabled
    if config.enable_file and config.log_file is not None:
        # Create log directory if it doesn't exist
        log_dir = config.log_file.parent
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise OSError(
                    f"Failed to create log directory '{log_dir}': {e}"
                ) from e
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(config.log_file),
            maxBytes=config.max_file_size,
            backupCount=config.backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Log configuration details
    root_logger.info(
        f"Logging configured: level={config.log_level}, "
        f"console={config.enable_console}, "
        f"file={config.enable_file}"
    )
    
    if config.enable_file and config.log_file:
        root_logger.info(
            f"Log file: {config.log_file} "
            f"(max_size={config.max_file_size / (1024 * 1024):.1f}MB, "
            f"backups={config.backup_count})"
        )


def get_logger(name: str) -> logging.Logger:
    """
    Get a module-specific logger instance.
    
    This function returns a logger configured with the module name,
    which will inherit the configuration from the root logger set up
    by setup_logging(). The module name appears in log messages,
    making it easy to identify the source of each log entry.
    
    Args:
        name: Logger name, typically __name__ of the calling module
    
    Returns:
        Logger instance configured for the specified module
    
    Example:
        >>> # In a module file
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
        >>> logger.debug("Processing data: %s", data)
        >>> logger.error("Failed to process", exc_info=True)
    
    Note:
        Always call setup_logging() before using get_logger() to ensure
        proper logging configuration. If setup_logging() has not been called,
        the logger will use Python's default configuration.
    """
    return logging.getLogger(name)
