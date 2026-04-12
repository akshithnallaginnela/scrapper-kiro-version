"""Unit tests for the logging system."""

import logging
import os
import tempfile
from pathlib import Path
import pytest

from src.logger import setup_logger, get_logger


def cleanup_logger(logger):
    """Helper function to cleanup logger handlers."""
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


class TestLoggingSystem:
    """Test cases for the logging system."""
    
    def test_setup_logger_creates_logger(self):
        """Test that setup_logger creates a logger instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(
                name="test_logger_1",
                log_file=log_file,
                log_level="INFO"
            )
            
            try:
                assert logger is not None
                assert isinstance(logger, logging.Logger)
                assert logger.name == "test_logger_1"
            finally:
                cleanup_logger(logger)
    
    def test_logger_has_dual_output(self):
        """Test that logger has both console and file handlers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(
                name="test_logger_2",
                log_file=log_file,
                log_level="INFO"
            )
            
            try:
                # Should have 2 handlers: console and file
                assert len(logger.handlers) == 2
                
                # Check handler types
                handler_types = [type(h).__name__ for h in logger.handlers]
                assert "StreamHandler" in handler_types
                assert "RotatingFileHandler" in handler_types
            finally:
                cleanup_logger(logger)
    
    def test_logger_respects_log_level(self):
        """Test that logger respects configured log level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            # Test DEBUG level
            logger_debug = setup_logger(
                name="test_logger_debug",
                log_file=log_file,
                log_level="DEBUG"
            )
            try:
                assert logger_debug.level == logging.DEBUG
            finally:
                cleanup_logger(logger_debug)
            
            # Test INFO level
            logger_info = setup_logger(
                name="test_logger_info",
                log_file=os.path.join(tmpdir, "test2.log"),
                log_level="INFO"
            )
            try:
                assert logger_info.level == logging.INFO
            finally:
                cleanup_logger(logger_info)
            
            # Test WARNING level
            logger_warning = setup_logger(
                name="test_logger_warning",
                log_file=os.path.join(tmpdir, "test3.log"),
                log_level="WARNING"
            )
            try:
                assert logger_warning.level == logging.WARNING
            finally:
                cleanup_logger(logger_warning)
            
            # Test ERROR level
            logger_error = setup_logger(
                name="test_logger_error",
                log_file=os.path.join(tmpdir, "test4.log"),
                log_level="ERROR"
            )
            try:
                assert logger_error.level == logging.ERROR
            finally:
                cleanup_logger(logger_error)
    
    def test_logger_creates_log_file(self):
        """Test that logger creates log file on disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(
                name="test_logger_3",
                log_file=log_file,
                log_level="INFO"
            )
            
            try:
                # Write a log message
                logger.info("Test message")
                
                # Flush handlers to ensure write
                for handler in logger.handlers:
                    handler.flush()
                
                # Check that log file was created
                assert os.path.exists(log_file)
                
                # Check that log file contains the message
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert "Test message" in content
                    assert "INFO" in content
            finally:
                cleanup_logger(logger)
    
    def test_logger_timestamp_formatting(self):
        """Test that log messages include timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(
                name="test_logger_4",
                log_file=log_file,
                log_level="INFO"
            )
            
            try:
                logger.info("Test timestamp")
                
                # Flush handlers
                for handler in logger.handlers:
                    handler.flush()
                
                # Read log file and check for timestamp format
                with open(log_file, 'r') as f:
                    content = f.read()
                    # Timestamp format: YYYY-MM-DD HH:MM:SS
                    import re
                    timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
                    assert re.search(timestamp_pattern, content) is not None
            finally:
                cleanup_logger(logger)
    
    def test_rotating_file_handler_configuration(self):
        """Test that rotating file handler is configured correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            max_size_mb = 10
            backup_count = 5
            
            logger = setup_logger(
                name="test_logger_5",
                log_file=log_file,
                log_level="INFO",
                max_log_size_mb=max_size_mb,
                backup_count=backup_count
            )
            
            try:
                # Find the RotatingFileHandler
                rotating_handler = None
                for handler in logger.handlers:
                    if isinstance(handler, logging.handlers.RotatingFileHandler):
                        rotating_handler = handler
                        break
                
                assert rotating_handler is not None
                assert rotating_handler.maxBytes == max_size_mb * 1024 * 1024
                assert rotating_handler.backupCount == backup_count
            finally:
                cleanup_logger(logger)
    
    def test_logger_creates_directory_if_not_exists(self):
        """Test that logger creates log directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "logs", "subdir", "test.log")
            logger = setup_logger(
                name="test_logger_6",
                log_file=log_file,
                log_level="INFO"
            )
            
            try:
                logger.info("Test message")
                
                # Flush handlers
                for handler in logger.handlers:
                    handler.flush()
                
                # Check that directory was created
                assert os.path.exists(os.path.dirname(log_file))
                assert os.path.exists(log_file)
            finally:
                cleanup_logger(logger)
    
    def test_get_logger_returns_existing_logger(self):
        """Test that get_logger returns existing logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            # Create logger
            logger1 = setup_logger(
                name="test_logger_7",
                log_file=log_file,
                log_level="INFO"
            )
            
            try:
                # Get the same logger
                logger2 = get_logger("test_logger_7")
                
                # Should be the same instance
                assert logger1 is logger2
            finally:
                cleanup_logger(logger1)
    
    def test_get_logger_creates_default_logger(self):
        """Test that get_logger creates logger with defaults if not exists."""
        logger = get_logger("test_logger_new")
        
        try:
            assert logger is not None
            assert isinstance(logger, logging.Logger)
            assert logger.name == "test_logger_new"
        finally:
            cleanup_logger(logger)
    
    def test_logger_prevents_duplicate_handlers(self):
        """Test that calling setup_logger twice doesn't create duplicate handlers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            
            # Setup logger twice
            logger1 = setup_logger(
                name="test_logger_8",
                log_file=log_file,
                log_level="INFO"
            )
            logger2 = setup_logger(
                name="test_logger_8",
                log_file=log_file,
                log_level="INFO"
            )
            
            try:
                # Should still have only 2 handlers
                assert len(logger1.handlers) == 2
                assert logger1 is logger2
            finally:
                cleanup_logger(logger1)
