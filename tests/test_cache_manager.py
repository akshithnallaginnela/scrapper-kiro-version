"""Tests for CacheManager - test mode with cached responses."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.cache_manager import CacheManager


class TestCacheManager:
    """Test suite for CacheManager functionality."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cache_manager(self, temp_cache_dir):
        """Create a CacheManager instance with temporary directory."""
        return CacheManager(cache_directory=temp_cache_dir)
    
    def test_cache_directory_creation(self, temp_cache_dir):
        """Test that cache directory is created if it doesn't exist."""
        cache_dir = Path(temp_cache_dir) / "new_cache"
        assert not cache_dir.exists()
        
        manager = CacheManager(cache_directory=str(cache_dir))
        assert cache_dir.exists()
    
    def test_generate_cache_key(self, cache_manager):
        """Test cache key generation from URL and source name."""
        url = "https://www.amazon.com/s?k=organic+products"
        source_name = "Amazon Organic Products"
        
        key = cache_manager._generate_cache_key(url, source_name)
        
        # Key should be filename-safe
        assert " " not in key
        assert "/" not in key
        assert "\\" not in key
        
        # Key should contain sanitized source name
        assert "Amazon" in key or "amazon" in key.lower()
        
        # Key should be consistent
        key2 = cache_manager._generate_cache_key(url, source_name)
        assert key == key2
    
    def test_save_and_retrieve_cached_html(self, cache_manager):
        """Test saving and retrieving cached HTML content."""
        url = "https://example.com/products"
        source_name = "Example Source"
        html_content = "<html><body><h1>Test Product</h1></body></html>"
        
        # Save HTML
        success = cache_manager.save_cached_html(url, source_name, html_content)
        assert success
        
        # Retrieve HTML
        retrieved_html = cache_manager.get_cached_html(url, source_name)
        assert retrieved_html == html_content
    
    def test_save_cached_html_with_metadata(self, cache_manager):
        """Test saving cached HTML with metadata."""
        url = "https://example.com/products"
        source_name = "Example Source"
        html_content = "<html><body><h1>Test</h1></body></html>"
        metadata = {
            "cached_at": datetime.now().isoformat(),
            "description": "Test cache entry"
        }
        
        # Save with metadata
        success = cache_manager.save_cached_html(
            url, source_name, html_content, metadata
        )
        assert success
        
        # Retrieve metadata
        retrieved_metadata = cache_manager.get_cache_metadata(url, source_name)
        assert retrieved_metadata is not None
        assert retrieved_metadata["url"] == url
        assert retrieved_metadata["source_name"] == source_name
        assert "cached_at" in retrieved_metadata
        assert "description" in retrieved_metadata
    
    def test_cache_miss(self, cache_manager):
        """Test behavior when cached content doesn't exist."""
        url = "https://nonexistent.com/page"
        source_name = "Nonexistent Source"
        
        html = cache_manager.get_cached_html(url, source_name)
        assert html is None
        
        metadata = cache_manager.get_cache_metadata(url, source_name)
        assert metadata is None
    
    def test_list_cached_sources(self, cache_manager):
        """Test listing all cached sources."""
        # Initially empty
        sources = cache_manager.list_cached_sources()
        assert len(sources) == 0
        
        # Add some cached entries
        cache_manager.save_cached_html(
            "https://example1.com", "Source 1", "<html>1</html>",
            {"cached_at": datetime.now().isoformat()}
        )
        cache_manager.save_cached_html(
            "https://example2.com", "Source 2", "<html>2</html>",
            {"cached_at": datetime.now().isoformat()}
        )
        
        # List should contain both sources
        sources = cache_manager.list_cached_sources()
        assert len(sources) == 2
        
        source_names = [name for name, _ in sources]
        assert "Source 1" in source_names
        assert "Source 2" in source_names
    
    def test_clear_cache(self, cache_manager):
        """Test clearing all cached files."""
        # Add some cached entries with metadata
        cache_manager.save_cached_html(
            "https://example1.com", "Source 1", "<html>1</html>",
            {"cached_at": "2024-01-15T10:00:00Z"}
        )
        cache_manager.save_cached_html(
            "https://example2.com", "Source 2", "<html>2</html>",
            {"cached_at": "2024-01-15T10:00:00Z"}
        )
        
        # Verify entries exist
        sources = cache_manager.list_cached_sources()
        assert len(sources) == 2
        
        # Clear cache
        success = cache_manager.clear_cache()
        assert success
        
        # Verify cache is empty
        sources = cache_manager.list_cached_sources()
        assert len(sources) == 0
    
    def test_utf8_encoding(self, cache_manager):
        """Test that UTF-8 content is handled correctly."""
        url = "https://example.com/unicode"
        source_name = "Unicode Source"
        html_content = "<html><body><p>Unicode: 你好 مرحبا שלום</p></body></html>"
        
        # Save and retrieve
        cache_manager.save_cached_html(url, source_name, html_content)
        retrieved = cache_manager.get_cached_html(url, source_name)
        
        assert retrieved == html_content
        assert "你好" in retrieved
        assert "مرحبا" in retrieved
        assert "שלום" in retrieved


class TestCacheManagerWithRealData:
    """Test CacheManager with actual test_data directory."""
    
    @pytest.fixture
    def real_cache_manager(self):
        """Create CacheManager pointing to actual test_data directory."""
        return CacheManager(cache_directory="./test_data")
    
    def test_load_existing_amazon_cache(self, real_cache_manager):
        """Test loading existing Amazon cached HTML."""
        url = "https://www.amazon.com/s?k=organic+products"
        source_name = "Amazon Organic Products"
        
        html = real_cache_manager.get_cached_html(url, source_name)
        
        # Should load the cached file
        assert html is not None
        assert len(html) > 0
        assert "Organic" in html
        assert "s-result-item" in html
    
    def test_load_existing_flipkart_cache(self, real_cache_manager):
        """Test loading existing Flipkart cached HTML."""
        url = "https://www.flipkart.com/search?q=organic+products"
        source_name = "Flipkart Organic"
        
        html = real_cache_manager.get_cached_html(url, source_name)
        
        # Should load the cached file
        assert html is not None
        assert len(html) > 0
        assert "Organic" in html
        assert "_1AtVbE" in html
    
    def test_load_existing_indiamart_cache(self, real_cache_manager):
        """Test loading existing IndiaMART cached HTML."""
        url = "https://www.indiamart.com/impcat/organic-products.html"
        source_name = "IndiaMART B2B Organic"
        
        html = real_cache_manager.get_cached_html(url, source_name)
        
        # Should load the cached file
        assert html is not None
        assert len(html) > 0
        assert "Organic" in html
        assert "lst" in html
    
    def test_list_real_cached_sources(self, real_cache_manager):
        """Test listing sources from actual test_data directory."""
        sources = real_cache_manager.list_cached_sources()
        
        # Should have at least 3 sources
        assert len(sources) >= 3
        
        source_names = [name for name, _ in sources]
        assert "Amazon Organic Products" in source_names
        assert "Flipkart Organic" in source_names
        assert "IndiaMART B2B Organic" in source_names
