"""Logging system for the Organic Products Web Scraper."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "organic_scraper",
    log_file: str = "scraper.log",
    log_level: str = "INFO",
    max_log_size_mb: int = 10,
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging system with dual output (console and rotating file).
    
    Args:
        name: Logger name
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_log_size_mb: Maximum log file size in megabytes before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger
    
    # Create formatters with timestamp
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Rotating file handler
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert MB to bytes
    max_bytes = max_log_size_mb * 1024 * 1024
    
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.
    
    Args:
        name: Logger name (defaults to "organic_scraper")
        
    Returns:
        Logger instance
    """
    logger_name = name or "organic_scraper"
    logger = logging.getLogger(logger_name)
    
    # If logger doesn't have handlers, set it up with defaults
    if not logger.handlers:
        return setup_logger(name=logger_name)
    
    return logger
