"""Unit tests for Configuration Manager."""

import pytest
import json
import yaml
import tempfile
import os
from pathlib import Path

from src.config_manager import ConfigurationManager
from src.models import ScraperConfiguration


class TestConfigurationManager:
    """Test suite for ConfigurationManager class."""
    
    def test_load_default_config_when_no_path_provided(self):
        """Test that default configuration is loaded when no path is provided."""
        config_manager = ConfigurationManager()
        
        assert config_manager.config is not None
        assert isinstance(config_manager.config, ScraperConfiguration)
        assert config_manager.config.timeout == 30
        assert config_manager.config.retry_attempts == 3
        assert config_manager.config.output_directory == "./output"
        assert config_manager.config.browser_type == "chrome"
        assert config_manager.config.headless is True
    
    def test_load_json_config(self):
        """Test loading configuration from JSON file."""
        config_data = {
            "sources": [
                {
                    "name": "Test Source",
                    "url": "https://example.com",
                    "type": "beautifulsoup"
                }
            ],
            "timeout": 60,
            "retry_attempts": 5,
            "output_directory": "./test_output",
            "browser_type": "firefox"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config_manager = ConfigurationManager(config_path=temp_path)
            
            assert len(config_manager.get_sources()) == 1
            assert config_manager.get_sources()[0]["name"] == "Test Source"
            assert config_manager.get_timeout() == 60
            assert config_manager.get_retry_attempts() == 5
            assert config_manager.get_output_directory() == "./test_output"
            assert config_manager.get_browser_type() == "firefox"
        finally:
            os.unlink(temp_path)
    
    def test_load_yaml_config(self):
        """Test loading configuration from YAML file."""
        config_data = {
            "sources": [
                {
                    "name": "YAML Test Source",
                    "url": "https://example.com",
                    "type": "selenium"
                }
            ],
            "timeout": 45,
            "retry_attempts": 2
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            config_manager = ConfigurationManager(config_path=temp_path)
            
            assert len(config_manager.get_sources()) == 1
            assert config_manager.get_sources()[0]["name"] == "YAML Test Source"
            assert config_manager.get_timeout() == 45
            assert config_manager.get_retry_attempts() == 2
        finally:
            os.unlink(temp_path)
    
    def test_file_not_found_uses_defaults(self):
        """Test that default values are used when config file is not found."""
        config_manager = ConfigurationManager(config_path="nonexistent.json")
        
        # Should fall back to defaults
        assert config_manager.config.timeout == 30
        assert config_manager.config.retry_attempts == 3
    
    def test_invalid_json_uses_defaults(self):
        """Test that default values are used when JSON is invalid."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            config_manager = ConfigurationManager(config_path=temp_path)
            
            # Should fall back to defaults
            assert config_manager.config.timeout == 30
        finally:
            os.unlink(temp_path)
    
    def test_unsupported_file_format_uses_defaults(self):
        """Test that default values are used for unsupported file formats."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("some text")
            temp_path = f.name
        
        try:
            config_manager = ConfigurationManager(config_path=temp_path)
            
            # Should fall back to defaults
            assert config_manager.config.timeout == 30
        finally:
            os.unlink(temp_path)
    
    def test_validation_invalid_timeout(self):
        """Test validation rejects invalid timeout values."""
        config_data = {
            "sources": [],
            "timeout": -10
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config_manager = ConfigurationManager(config_path=temp_path)
            # Should fall back to defaults due to validation error
            assert config_manager.config.timeout == 30
        finally:
            os.unlink(temp_path)
    
    def test_validation_invalid_browser_type(self):
        """Test validation rejects invalid browser types."""
        config_data = {
            "sources": [],
            "browser_type": "safari"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config_manager = ConfigurationManager(config_path=temp_path)
            # Should fall back to defaults due to validation error
            assert config_manager.config.browser_type == "chrome"
        finally:
            os.unlink(temp_path)
    
    def test_validation_request_delay_min_greater_than_max(self):
        """Test validation rejects when min delay is greater than max delay."""
        config_data = {
            "sources": [],
            "request_delay_min": 5.0,
            "request_delay_max": 2.0
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config_manager = ConfigurationManager(config_path=temp_path)
            # Should fall back to defaults due to validation error
            assert config_manager.config.request_delay_min == 1.0
            assert config_manager.config.request_delay_max == 3.0
        finally:
            os.unlink(temp_path)
    
    def test_validation_sources_missing_required_fields(self):
        """Test validation rejects sources missing required fields."""
        config_data = {
            "sources": [
                {
                    "name": "Test Source"
                    # Missing 'url' field
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config_manager = ConfigurationManager(config_path=temp_path)
            # Should fall back to defaults due to validation error
            assert config_manager.config.sources == []
        finally:
            os.unlink(temp_path)
    
    def test_getter_methods(self):
        """Test all getter methods return correct values."""
        config_data = {
            "sources": [{"name": "Test", "url": "https://example.com"}],
            "timeout": 50,
            "retry_attempts": 4,
            "output_directory": "./custom_output",
            "browser_type": "firefox",
            "headless": False,
            "request_delay_min": 2.0,
            "request_delay_max": 5.0,
            "max_concurrent_requests": 10,
            "log_level": "DEBUG",
            "log_file": "custom.log",
            "max_log_size_mb": 20
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config_manager = ConfigurationManager(config_path=temp_path)
            
            assert config_manager.get_sources() == [{"name": "Test", "url": "https://example.com"}]
            assert config_manager.get_timeout() == 50
            assert config_manager.get_retry_attempts() == 4
            assert config_manager.get_output_directory() == "./custom_output"
            assert config_manager.get_browser_type() == "firefox"
            assert config_manager.get_headless() is False
            assert config_manager.get_request_delay_min() == 2.0
            assert config_manager.get_request_delay_max() == 5.0
            assert config_manager.get_max_concurrent_requests() == 10
            assert config_manager.get_log_level() == "DEBUG"
            assert config_manager.get_log_file() == "custom.log"
            assert config_manager.get_max_log_size_mb() == 20
            assert isinstance(config_manager.get_config(), ScraperConfiguration)
        finally:
            os.unlink(temp_path)
    
    def test_merge_with_defaults(self):
        """Test that partial configuration is merged with defaults."""
        config_data = {
            "timeout": 100
            # Only timeout specified, other values should use defaults
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config_manager = ConfigurationManager(config_path=temp_path)
            
            assert config_manager.get_timeout() == 100  # Custom value
            assert config_manager.get_retry_attempts() == 3  # Default value
            assert config_manager.get_browser_type() == "chrome"  # Default value
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
