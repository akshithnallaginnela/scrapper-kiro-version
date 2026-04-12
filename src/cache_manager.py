"""Cache manager for test mode with cached HTML responses."""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import logging


class CacheManager:
    """Manages cached HTML responses for test mode."""
    
    def __init__(self, cache_directory: str = "./test_data", logger: Optional[logging.Logger] = None):
        """
        Initialize cache manager.
        
        Args:
            cache_directory: Directory to store cached HTML files
            logger: Logger instance for logging cache operations
        """
        self.cache_directory = Path(cache_directory)
        self.logger = logger or logging.getLogger(__name__)
        self._ensure_cache_directory()
    
    def _ensure_cache_directory(self) -> None:
        """Create cache directory if it doesn't exist."""
        try:
            self.cache_directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Cache directory ensured: {self.cache_directory}")
        except Exception as e:
            self.logger.error(f"Failed to create cache directory: {e}")
            raise
    
    def _generate_cache_key(self, url: str, source_name: str) -> str:
        """
        Generate a cache key from URL and source name.
        
        Args:
            url: The URL being cached
            source_name: Name of the source
            
        Returns:
            Cache key (filename-safe string)
        """
        # Create a hash of the URL for uniqueness
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
        
        # Sanitize source name for filename
        safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in source_name)
        
        return f"{safe_name}_{url_hash}"
    
    def get_cached_html(self, url: str, source_name: str) -> Optional[str]:
        """
        Retrieve cached HTML for a given URL and source.
        
        Args:
            url: The URL to retrieve cached HTML for
            source_name: Name of the source
            
        Returns:
            Cached HTML content if found, None otherwise
        """
        cache_key = self._generate_cache_key(url, source_name)
        cache_file = self.cache_directory / f"{cache_key}.html"
        
        if not cache_file.exists():
            self.logger.debug(f"Cache miss for {source_name}: {cache_file}")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.logger.info(f"Cache hit for {source_name}: {cache_file}")
            return html_content
            
        except Exception as e:
            self.logger.error(f"Failed to read cache file {cache_file}: {e}")
            return None
    
    def save_cached_html(self, url: str, source_name: str, html_content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save HTML content to cache.
        
        Args:
            url: The URL being cached
            source_name: Name of the source
            html_content: HTML content to cache
            metadata: Optional metadata to save alongside HTML
            
        Returns:
            True if successful, False otherwise
        """
        cache_key = self._generate_cache_key(url, source_name)
        cache_file = self.cache_directory / f"{cache_key}.html"
        metadata_file = self.cache_directory / f"{cache_key}.json"
        
        try:
            # Save HTML content
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Save metadata if provided
            if metadata:
                metadata_dict = {
                    'url': url,
                    'source_name': source_name,
                    **metadata
                }
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata_dict, f, indent=2)
            
            self.logger.info(f"Cached HTML for {source_name}: {cache_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save cache file {cache_file}: {e}")
            return False
    
    def get_cache_metadata(self, url: str, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a cached entry.
        
        Args:
            url: The URL to retrieve metadata for
            source_name: Name of the source
            
        Returns:
            Metadata dictionary if found, None otherwise
        """
        cache_key = self._generate_cache_key(url, source_name)
        metadata_file = self.cache_directory / f"{cache_key}.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to read metadata file {metadata_file}: {e}")
            return None
    
    def clear_cache(self) -> bool:
        """
        Clear all cached files.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            for file in self.cache_directory.glob('*'):
                if file.is_file():
                    file.unlink()
            
            self.logger.info("Cache cleared successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return False
    
    def list_cached_sources(self) -> list:
        """
        List all cached sources.
        
        Returns:
            List of tuples (source_name, cache_key)
        """
        cached_sources = []
        
        for metadata_file in self.cache_directory.glob('*.json'):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    source_name = metadata.get('source_name', 'Unknown')
                    cache_key = metadata_file.stem
                    cached_sources.append((source_name, cache_key))
            except Exception as e:
                self.logger.warning(f"Failed to read metadata file {metadata_file}: {e}")
        
        return cached_sources
