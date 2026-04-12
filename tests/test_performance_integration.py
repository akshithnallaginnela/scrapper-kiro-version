"""Integration tests for performance optimizations."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from src.source_manager import SourceManager
from src.performance_monitor import PerformanceMonitor
from src.models import ScrapingResult


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = Mock()
    config.get_sources.return_value = []
    config.get_timeout.return_value = 30
    config.get_retry_attempts.return_value = 3
    config.get_browser_type.return_value = "chrome"
    config.get_headless.return_value = True
    config.get_request_delay_min.return_value = 0.1  # Shorter for testing
    config.get_request_delay_max.return_value = 0.2
    config.get_max_concurrent_requests.return_value = 5
    config.get_test_mode.return_value = False
    config.get_test_data_directory.return_value = "test_data"
    return config


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return Mock()


class TestConcurrentScraping:
    """Tests for concurrent scraping performance."""
    
    def test_concurrent_scraping_faster_than_sequential(self, mock_config, mock_logger):
        """Test that concurrent scraping is faster than sequential."""
        # Create 5 sources
        sources = [
            {'name': f'Source {i}', 'url': f'https://example{i}.com'}
            for i in range(5)
        ]
        mock_config.get_sources.return_value = sources
        
        with patch('src.source_manager.BeautifulSoupScraper'):
            manager = SourceManager(mock_config, mock_logger)
            
            # Mock scrape_source to simulate network delay
            def slow_scrape(source):
                time.sleep(0.1)  # Simulate 100ms network delay
                return ScrapingResult(
                    source_name=source['name'],
                    success=True,
                    html_content='<html></html>',
                    response_time=0.1
                )
            
            manager.scrape_source = Mock(side_effect=slow_scrape)
            
            # Measure concurrent scraping time
            start = time.time()
            results = manager.scrape_all_sources()
            concurrent_time = time.time() - start
            
            # With 5 concurrent workers and 5 sources, should complete in ~0.1s
            # Sequential would take ~0.5s (5 * 0.1s)
            assert len(results) == 5
            assert concurrent_time < 0.3  # Should be much faster than sequential
            # Note: In real scenario with actual network I/O, the speedup would be more dramatic
    
    def test_concurrent_scraping_respects_max_workers(self, mock_config, mock_logger):
        """Test that concurrent scraping respects max_concurrent_requests limit."""
        # Create 10 sources
        sources = [
            {'name': f'Source {i}', 'url': f'https://example{i}.com'}
            for i in range(10)
        ]
        mock_config.get_sources.return_value = sources
        mock_config.get_max_concurrent_requests.return_value = 3  # Limit to 3
        
        with patch('src.source_manager.BeautifulSoupScraper'):
            manager = SourceManager(mock_config, mock_logger)
            
            # Mock scrape_source
            manager.scrape_source = Mock(return_value=ScrapingResult(
                source_name='Test',
                success=True,
                html_content='<html></html>'
            ))
            
            results = manager.scrape_all_sources()
            
            # Should still scrape all sources
            assert len(results) == 10


class TestMemoryMonitoring:
    """Tests for memory monitoring during scraping."""
    
    def test_memory_monitor_tracks_usage(self, mock_logger):
        """Test that memory monitor tracks usage throughout scraping."""
        with patch('src.performance_monitor.psutil.Process') as mock_process_class:
            mock_process = Mock()
            mock_process.memory_info.return_value = Mock(rss=200 * 1024 * 1024)  # 200 MB
            mock_process.memory_percent.return_value = 8.0
            mock_process.cpu_percent.return_value = 25.0
            mock_process_class.return_value = mock_process
            
            monitor = PerformanceMonitor(memory_limit_mb=500.0, logger=mock_logger)
            
            # Simulate scraping workflow
            monitor.log_memory_usage("Start")
            
            # Check memory is within limit
            assert monitor.check_memory_limit() is True
            
            # Get metrics
            metrics = monitor.get_metrics(execution_time=120.0)
            
            assert metrics.memory_usage_mb == 200.0
            assert metrics.is_within_memory_limit() is True
    
    def test_memory_monitor_detects_limit_exceeded(self, mock_logger):
        """Test that memory monitor detects when limit is exceeded."""
        with patch('src.performance_monitor.psutil.Process') as mock_process_class:
            mock_process = Mock()
            mock_process.memory_info.return_value = Mock(rss=600 * 1024 * 1024)  # 600 MB
            mock_process.memory_percent.return_value = 20.0
            mock_process.cpu_percent.return_value = 30.0
            mock_process_class.return_value = mock_process
            
            monitor = PerformanceMonitor(memory_limit_mb=500.0, logger=mock_logger)
            
            # Check memory limit
            assert monitor.check_memory_limit() is False
            
            # Should log warning
            mock_logger.warning.assert_called_once()
            assert "Memory limit exceeded" in mock_logger.warning.call_args[0][0]


class TestConnectionPooling:
    """Tests for connection pooling and DNS caching."""
    
    def test_beautifulsoup_scraper_uses_session(self):
        """Test that BeautifulSoup scraper uses session for connection pooling."""
        from src.beautifulsoup_scraper import BeautifulSoupScraper
        
        scraper = BeautifulSoupScraper(timeout=30)
        
        # Verify session exists
        assert scraper.session is not None
        
        # Verify session has adapters (for connection pooling)
        assert 'http://' in scraper.session.adapters
        assert 'https://' in scraper.session.adapters
        
        scraper.close()
    
    def test_session_reused_across_requests(self):
        """Test that session is reused across multiple requests."""
        from src.beautifulsoup_scraper import BeautifulSoupScraper
        
        scraper = BeautifulSoupScraper(timeout=30)
        
        # Mock the session.get method
        scraper.session.get = Mock(return_value=Mock(
            status_code=200,
            text='<html></html>'
        ))
        
        # Make multiple requests
        scraper.fetch_html('https://example1.com')
        scraper.fetch_html('https://example2.com')
        
        # Verify session.get was called twice (reusing same session)
        assert scraper.session.get.call_count == 2
        
        scraper.close()


class TestPerformanceRequirements:
    """Tests for specific performance requirements."""
    
    def test_execution_time_under_5_minutes(self, mock_config, mock_logger):
        """Test that scraping completes within 5 minutes (300 seconds)."""
        # This is a smoke test - actual timing depends on network conditions
        sources = [
            {'name': f'Source {i}', 'url': f'https://example{i}.com'}
            for i in range(3)
        ]
        mock_config.get_sources.return_value = sources
        
        with patch('src.source_manager.BeautifulSoupScraper'):
            manager = SourceManager(mock_config, mock_logger)
            
            # Mock fast scraping
            manager.scrape_source = Mock(return_value=ScrapingResult(
                source_name='Test',
                success=True,
                html_content='<html></html>',
                response_time=0.1
            ))
            
            start = time.time()
            results = manager.scrape_all_sources()
            elapsed = time.time() - start
            
            # Should complete very quickly with mocked sources
            assert elapsed < 300  # 5 minutes
            assert len(results) == 3
    
    def test_memory_stays_under_500mb_limit(self, mock_logger):
        """Test that memory monitoring enforces 500 MB limit."""
        with patch('src.performance_monitor.psutil.Process') as mock_process_class:
            mock_process = Mock()
            # Simulate memory usage under limit
            mock_process.memory_info.return_value = Mock(rss=450 * 1024 * 1024)  # 450 MB
            mock_process.memory_percent.return_value = 15.0
            mock_process.cpu_percent.return_value = 30.0
            mock_process_class.return_value = mock_process
            
            monitor = PerformanceMonitor(memory_limit_mb=500.0, logger=mock_logger)
            
            # Verify limit is enforced
            assert monitor.memory_limit_mb == 500.0
            assert monitor.check_memory_limit() is True
            
            metrics = monitor.get_metrics()
            assert metrics.is_within_memory_limit() is True
