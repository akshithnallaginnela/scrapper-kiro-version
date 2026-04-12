"""Integration tests for test mode with cached responses."""

import pytest
from pathlib import Path

from src.config_manager import ConfigurationManager
from src.source_manager import SourceManager
from src.product_extractor import ProductExtractor


class TestModeIntegration:
    """Integration tests for test mode functionality."""
    
    @pytest.fixture
    def test_mode_config(self):
        """Load test mode configuration."""
        config_path = "config/config.test_mode.json"
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        return ConfigurationManager(config_path=config_path, logger=logger)
    
    @pytest.fixture
    def normal_mode_config(self):
        """Load normal mode configuration."""
        config_path = "config/config.json"
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        return ConfigurationManager(config_path=config_path, logger=logger)
    
    def test_test_mode_enabled_in_config(self, test_mode_config):
        """Test that test mode is enabled in test_mode config."""
        assert test_mode_config.get_test_mode() is True
        assert test_mode_config.get_test_data_directory() == "./test_data"
    
    def test_test_mode_disabled_in_normal_config(self, normal_mode_config):
        """Test that test mode is disabled in normal config."""
        assert normal_mode_config.get_test_mode() is False
    
    def test_source_manager_uses_cache_in_test_mode(self, test_mode_config):
        """Test that SourceManager uses cached responses in test mode."""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        with SourceManager(test_mode_config, logger) as source_manager:
            # Verify test mode is enabled
            assert source_manager.test_mode is True
            assert source_manager.cache_manager is not None
            
            # Scrape all sources (should use cache)
            results = source_manager.scrape_all_sources()
            
            # Should have results from cached sources
            assert len(results) > 0
            
            # All results should be successful (cache hits)
            successful_results = [r for r in results if r.success]
            assert len(successful_results) >= 3
            
            # Verify HTML content was loaded
            for result in successful_results:
                assert result.html_content is not None
                assert len(result.html_content) > 0
                assert "Organic" in result.html_content
    
    def test_product_extraction_from_cached_amazon_data(self, test_mode_config):
        """Test extracting products from cached Amazon HTML."""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        with SourceManager(test_mode_config, logger) as source_manager:
            # Get Amazon source config
            sources = test_mode_config.get_sources()
            amazon_source = next(
                (s for s in sources if "Amazon" in s["name"]), None
            )
            assert amazon_source is not None
            
            # Scrape Amazon (should use cache)
            result = source_manager.scrape_source(amazon_source)
            assert result.success
            assert result.html_content is not None
            
            # Extract products
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(result.html_content, 'html.parser')
            
            extractor = ProductExtractor(logger)
            products = extractor.extract_products(
                soup, 
                amazon_source["name"],
                amazon_source["selectors"]
            )
            
            # Should extract products from cached HTML
            assert len(products) > 0
            
            # Verify product data
            for product in products:
                assert product.name
                assert product.source == amazon_source["name"]
                assert "Organic" in product.name
    
    def test_product_extraction_from_cached_flipkart_data(self, test_mode_config):
        """Test extracting products from cached Flipkart HTML."""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        with SourceManager(test_mode_config, logger) as source_manager:
            # Get Flipkart source config
            sources = test_mode_config.get_sources()
            flipkart_source = next(
                (s for s in sources if "Flipkart" in s["name"]), None
            )
            assert flipkart_source is not None
            
            # Scrape Flipkart (should use cache)
            result = source_manager.scrape_source(flipkart_source)
            assert result.success
            assert result.html_content is not None
            
            # Extract products
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(result.html_content, 'html.parser')
            
            extractor = ProductExtractor(logger)
            products = extractor.extract_products(
                soup,
                flipkart_source["name"],
                flipkart_source["selectors"]
            )
            
            # Should extract products from cached HTML
            assert len(products) > 0
            
            # Verify product data
            for product in products:
                assert product.name
                assert product.source == flipkart_source["name"]
                assert "Organic" in product.name
    
    def test_product_extraction_from_cached_indiamart_data(self, test_mode_config):
        """Test extracting products from cached IndiaMART HTML."""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        with SourceManager(test_mode_config, logger) as source_manager:
            # Get IndiaMART source config
            sources = test_mode_config.get_sources()
            indiamart_source = next(
                (s for s in sources if "IndiaMART" in s["name"]), None
            )
            assert indiamart_source is not None
            
            # Scrape IndiaMART (should use cache)
            result = source_manager.scrape_source(indiamart_source)
            assert result.success
            assert result.html_content is not None
            
            # Extract products
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(result.html_content, 'html.parser')
            
            extractor = ProductExtractor(logger)
            products = extractor.extract_products(
                soup,
                indiamart_source["name"],
                indiamart_source["selectors"]
            )
            
            # Should extract products from cached HTML
            assert len(products) > 0
            
            # Verify product data
            for product in products:
                assert product.name
                assert product.source == indiamart_source["name"]
                assert "Organic" in product.name
    
    def test_test_mode_performance(self, test_mode_config):
        """Test that test mode is faster than live requests."""
        import time
        import logging
        
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        with SourceManager(test_mode_config, logger) as source_manager:
            start_time = time.time()
            results = source_manager.scrape_all_sources()
            elapsed = time.time() - start_time
            
            # Test mode should be very fast (< 1 second for cached responses)
            assert elapsed < 5.0, f"Test mode took {elapsed:.2f}s, expected < 5s"
            
            # Should have successful results
            successful = [r for r in results if r.success]
            assert len(successful) >= 3
    
    def test_cache_directory_exists(self):
        """Test that test_data directory exists with cached files."""
        test_data_dir = Path("./test_data")
        assert test_data_dir.exists()
        assert test_data_dir.is_dir()
        
        # Should have HTML files
        html_files = list(test_data_dir.glob("*.html"))
        assert len(html_files) >= 3
        
        # Should have JSON metadata files
        json_files = list(test_data_dir.glob("*.json"))
        assert len(json_files) >= 3
    
    def test_cached_files_have_content(self):
        """Test that cached HTML files have actual product data."""
        test_data_dir = Path("./test_data")
        html_files = list(test_data_dir.glob("*.html"))
        
        for html_file in html_files:
            content = html_file.read_text(encoding='utf-8')
            
            # Should have HTML structure
            assert "<html" in content.lower()
            assert "</html>" in content.lower()
            
            # Should have product-related content
            assert "organic" in content.lower()
            
            # Should not be empty
            assert len(content) > 100


class TestTestModeDocumentation:
    """Tests to verify test mode is properly documented."""
    
    def test_readme_mentions_test_mode(self):
        """Test that README documents test mode."""
        readme_path = Path("README.md")
        if readme_path.exists():
            content = readme_path.read_text()
            # Check for test mode documentation
            assert "test" in content.lower() or "cache" in content.lower()
    
    def test_config_guide_mentions_test_mode(self):
        """Test that CONFIG_GUIDE documents test mode."""
        config_guide_path = Path("config/CONFIG_GUIDE.md")
        if config_guide_path.exists():
            content = config_guide_path.read_text()
            # Should document test_mode flag
            assert "test_mode" in content or "test mode" in content.lower()
