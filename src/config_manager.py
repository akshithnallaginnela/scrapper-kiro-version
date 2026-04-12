"""Configuration management for the Organic Products Web Scraper."""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict
import logging

from src.models import ScraperConfiguration


class ConfigurationManager:
    """Manages application configuration from files or defaults."""
    
    def __init__(self, config_path: Optional[str] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file (JSON or YAML)
            logger: Logger instance for logging configuration events
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config: ScraperConfiguration = self._load_default_config()
        
        if config_path:
            try:
                loaded_config = self.load_config(config_path)
                self.config = self._merge_with_defaults(loaded_config)
                self.logger.info(f"Configuration loaded successfully from {config_path}")
            except Exception as e:
                self.logger.warning(
                    f"Failed to load configuration from {config_path}: {e}. Using default values."
                )
        else:
            self.logger.warning("No configuration file provided. Using default values.")
    
    def _load_default_config(self) -> ScraperConfiguration:
        """Load default configuration values."""
        return ScraperConfiguration(
            sources=[],  # Empty by default, should be provided in config file
            timeout=30,
            retry_attempts=3,
            output_directory="./output",
            browser_type="chrome",
            headless=True,
            request_delay_min=1.0,
            request_delay_max=3.0,
            max_concurrent_requests=5,
            log_level="INFO",
            log_file="scraper.log",
            max_log_size_mb=10
        )
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from JSON or YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary containing configuration values
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If file format is not supported or invalid
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        file_extension = path.suffix.lower()
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if file_extension == '.json':
                    config_data = json.load(f)
                elif file_extension in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                else:
                    raise ValueError(
                        f"Unsupported configuration file format: {file_extension}. "
                        "Supported formats: .json, .yaml, .yml"
                    )
            
            # Validate configuration
            self._validate_config(config_data)
            
            return config_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")
    
    def _validate_config(self, config_data: Dict[str, Any]) -> None:
        """
        Validate configuration data.
        
        Args:
            config_data: Configuration dictionary to validate
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate timeout
        if 'timeout' in config_data:
            if not isinstance(config_data['timeout'], (int, float)) or config_data['timeout'] <= 0:
                raise ValueError("timeout must be a positive number")
        
        # Validate retry_attempts
        if 'retry_attempts' in config_data:
            if not isinstance(config_data['retry_attempts'], int) or config_data['retry_attempts'] < 0:
                raise ValueError("retry_attempts must be a non-negative integer")
        
        # Validate browser_type
        if 'browser_type' in config_data:
            valid_browsers = ['chrome', 'firefox']
            if config_data['browser_type'].lower() not in valid_browsers:
                raise ValueError(f"browser_type must be one of: {valid_browsers}")
        
        # Validate headless
        if 'headless' in config_data:
            if not isinstance(config_data['headless'], bool):
                raise ValueError("headless must be a boolean")
        
        # Validate request delays
        if 'request_delay_min' in config_data:
            if not isinstance(config_data['request_delay_min'], (int, float)) or config_data['request_delay_min'] < 0:
                raise ValueError("request_delay_min must be a non-negative number")
        
        if 'request_delay_max' in config_data:
            if not isinstance(config_data['request_delay_max'], (int, float)) or config_data['request_delay_max'] < 0:
                raise ValueError("request_delay_max must be a non-negative number")
        
        if 'request_delay_min' in config_data and 'request_delay_max' in config_data:
            if config_data['request_delay_min'] > config_data['request_delay_max']:
                raise ValueError("request_delay_min cannot be greater than request_delay_max")
        
        # Validate max_concurrent_requests
        if 'max_concurrent_requests' in config_data:
            if not isinstance(config_data['max_concurrent_requests'], int) or config_data['max_concurrent_requests'] <= 0:
                raise ValueError("max_concurrent_requests must be a positive integer")
        
        # Validate log_level
        if 'log_level' in config_data:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if config_data['log_level'].upper() not in valid_levels:
                raise ValueError(f"log_level must be one of: {valid_levels}")
        
        # Validate max_log_size_mb
        if 'max_log_size_mb' in config_data:
            if not isinstance(config_data['max_log_size_mb'], (int, float)) or config_data['max_log_size_mb'] <= 0:
                raise ValueError("max_log_size_mb must be a positive number")
        
        # Validate sources
        if 'sources' in config_data:
            if not isinstance(config_data['sources'], list):
                raise ValueError("sources must be a list")
            
            for idx, source in enumerate(config_data['sources']):
                if not isinstance(source, dict):
                    raise ValueError(f"Source at index {idx} must be a dictionary")
                
                required_fields = ['name', 'url']
                for field in required_fields:
                    if field not in source:
                        raise ValueError(f"Source at index {idx} missing required field: {field}")
    
    def _merge_with_defaults(self, config_data: Dict[str, Any]) -> ScraperConfiguration:
        """
        Merge loaded configuration with default values.
        
        Args:
            config_data: Loaded configuration dictionary
            
        Returns:
            ScraperConfiguration object with merged values
        """
        default_dict = asdict(self.config)
        
        # Update defaults with loaded values
        for key, value in config_data.items():
            if key in default_dict:
                default_dict[key] = value
        
        return ScraperConfiguration(**default_dict)
    
    # Getter methods for all configuration values
    
    def get_sources(self) -> List[Dict[str, str]]:
        """Return list of configured data sources."""
        return self.config.sources
    
    def get_timeout(self) -> int:
        """Return request timeout in seconds."""
        return self.config.timeout
    
    def get_retry_attempts(self) -> int:
        """Return number of retry attempts."""
        return self.config.retry_attempts
    
    def get_output_directory(self) -> str:
        """Return output directory path."""
        return self.config.output_directory
    
    def get_browser_type(self) -> str:
        """Return browser type for Selenium (chrome/firefox)."""
        return self.config.browser_type
    
    def get_headless(self) -> bool:
        """Return whether to run browser in headless mode."""
        return self.config.headless
    
    def get_request_delay_min(self) -> float:
        """Return minimum request delay in seconds."""
        return self.config.request_delay_min
    
    def get_request_delay_max(self) -> float:
        """Return maximum request delay in seconds."""
        return self.config.request_delay_max
    
    def get_max_concurrent_requests(self) -> int:
        """Return maximum number of concurrent requests."""
        return self.config.max_concurrent_requests
    
    def get_log_level(self) -> str:
        """Return logging level."""
        return self.config.log_level
    
    def get_log_file(self) -> str:
        """Return log file path."""
        return self.config.log_file
    
    def get_max_log_size_mb(self) -> int:
        """Return maximum log file size in megabytes."""
        return self.config.max_log_size_mb
    
    def get_test_mode(self) -> bool:
        """Return whether test mode is enabled."""
        return self.config.test_mode
    
    def get_test_data_directory(self) -> str:
        """Return test data directory path."""
        return self.config.test_data_directory
    
    def get_config(self) -> ScraperConfiguration:
        """Return the complete configuration object."""
        return self.config
