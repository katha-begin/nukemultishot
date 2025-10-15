"""
Logging utilities for the Multishot Workflow System.

Provides centralized logging with file and console output.
"""

import os
import logging
import sys
from typing import Optional
from datetime import datetime

# Global logger instances
_loggers = {}
_log_file = None
_log_level = logging.INFO

def setup_logging(log_level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """Setup global logging configuration."""
    global _log_level, _log_file
    
    _log_level = log_level
    _log_file = log_file
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger('multishot')
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            # Ensure log directory exists
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            root_logger.info(f"Logging to file: {log_file}")
            
        except Exception as e:
            root_logger.error(f"Failed to setup file logging: {e}")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module."""
    global _loggers
    
    if name not in _loggers:
        # Create logger with multishot prefix
        logger_name = f"multishot.{name}" if not name.startswith('multishot') else name
        logger = logging.getLogger(logger_name)
        
        # Set level from global setting
        logger.setLevel(_log_level)
        
        # Store in cache
        _loggers[name] = logger
    
    return _loggers[name]

def get_default_log_file() -> str:
    """Get the default log file path."""
    try:
        # Try to get Nuke's user directory
        import nuke
        nuke_dir = nuke.value("preferences.nuke_user_dir")
        if nuke_dir:
            log_dir = os.path.join(nuke_dir, "multishot", "logs")
        else:
            # Fallback to temp directory
            import tempfile
            log_dir = os.path.join(tempfile.gettempdir(), "multishot", "logs")
    except ImportError:
        # Not in Nuke environment, use temp directory
        import tempfile
        log_dir = os.path.join(tempfile.gettempdir(), "multishot", "logs")
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"multishot_{timestamp}.log")
    
    return log_file

def set_log_level(level: int) -> None:
    """Set the global log level."""
    global _log_level
    _log_level = level
    
    # Update all existing loggers
    for logger in _loggers.values():
        logger.setLevel(level)
    
    # Update root logger
    root_logger = logging.getLogger('multishot')
    root_logger.setLevel(level)
    for handler in root_logger.handlers:
        handler.setLevel(level)

def log_exception(logger: logging.Logger, message: str = "An error occurred") -> None:
    """Log an exception with full traceback."""
    import traceback
    logger.error(f"{message}: {traceback.format_exc()}")

def log_performance(logger: logging.Logger, operation: str, duration: float) -> None:
    """Log performance information."""
    logger.info(f"Performance: {operation} took {duration:.3f} seconds")

# Context manager for performance logging
class PerformanceLogger:
    """Context manager for logging operation performance."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        
        if exc_type is None:
            log_performance(self.logger, self.operation, duration)
        else:
            self.logger.error(f"Failed: {self.operation} after {duration:.3f} seconds")
        
        return False  # Don't suppress exceptions

# Initialize default logging
try:
    default_log_file = get_default_log_file()
    setup_logging(logging.INFO, default_log_file)
except Exception:
    # Fallback to console-only logging
    setup_logging(logging.INFO, None)
