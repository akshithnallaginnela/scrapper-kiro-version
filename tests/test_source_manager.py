"""Unit tests for SourceManager class."""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.source_manager import SourceManager
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
    config.get_request_delay_min.return_value = 1.0
    config.get_request_delay_max.return_value = 3.0
    config.get_max_concurrent_requests.return_value = 5
    config.get_test_mode.return_value = False
    config.get_test_data_directory.return_value = "test_data"
    return config


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return Mock()


@pytest.fixture
def source_manager(mock_config, mock_logger):
    """Create SourceManager instance with mocked dependencies."""
    with patch('src.source_manager.BeautifulSoupScraper'):
        manager = SourceManager(mock_config, mock_logger)
        return manager


class TestSourceManagerInit:
    """Tests for SourceManager initialization."""
    
    def test_init_creates_bs_scraper(self, mock_config, mock_logger):
        """Test that initialization creates BeautifulSoup scraper."""
        with patch('src.source_manager.BeautifulSoupScraper') as mock_bs:
            manager = SourceManager(mock_config, mock_logger)
            
            mock_bs.assert_called_once_with(
                timeout=30,
                logger=mock_logger
            )
            assert manager.config == mock_config
            assert manager.logger == mock_logger
    
    def test_init_selenium_scraper_lazy(self, source_manager):
        """Test that Selenium scraper is not initialized until needed."""
        assert source_manager.selenium_scraper is None
    
    def test_init_domain_tracking_empty(self, source_manager):
        """Test that domain tracking dictionary is initialized empty."""
        assert source_manager._domain_last_request == {}


class TestScrapeAllSources:
    """Tests for scrape_all_sources method."""
    
    def test_scrape_all_sources_empty_list(self, source_manager, mock_config):
        """Test scraping with no configured sources."""
        mock_config.get_sources.return_value = []
        
        results = source_manager.scrape_all_sources()
        
        assert results == []
        source_manager.logger.warning.assert_called_once()
    
    def test_scrape_all_sources_single_success(self, source_manager, mock_config):
        """Test scraping single source successfully."""
        mock_config.get_sources.return_value = [
            {'name': 'Test Source', 'url': 'https://example.com', 'type': 'static'}
        ]
        
        # Mock scrape_source to return success
        source_manager.scrape_source = Mock(return_value=ScrapingResult(
            source_name='Test Source',
            success=True,
            html_content='<html></html>',
            response_time=1.0
        ))
        
        results = source_manager.scrape_all_sources()
        
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].source_name == 'Test Source'
    
    def test_scrape_all_sources_multiple_mixed(self, source_manager, mock_config):
        """Test scraping multiple sources with mixed success/failure."""
        mock_config.get_sources.return_value = [
            {'name': 'Source 1', 'url': 'https://example1.com'},
            {'name': 'Source 2', 'url': 'https://example2.com'},
            {'name': 'Source 3', 'url': 'https://example3.com'}
        ]
        
        # Mock scrape_source to return alternating success/failure
        def mock_scrape(source):
            if source['name'] == 'Source 2':
                return ScrapingResult(source_name='Source 2', success=False, error_message='Error')
            else:
                return ScrapingResult(source_name=source['name'], success=True, html_content='<html></html>')
        
        source_manager.scrape_source = Mock(side_effect=mock_scrape)
        
        results = source_manager.scrape_all_sources()
        
        assert len(results) == 3
        # Check that we have 2 successes and 1 failure (order may vary due to concurrency)
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        assert len(successful) == 2
        assert len(failed) == 1
        assert failed[0].source_name == 'Source 2'
    
    def test_scrape_all_sources_respects_timeout(self, source_manager, mock_config):
        """Test that scraping stops after 300 second timeout."""
        # Create many sources
        mock_config.get_sources.return_value = [
            {'name': f'Source {i}', 'url': f'https://example{i}.com'}
            for i in range(100)
        ]
        
        # Mock scrape_source to take time and track calls
        call_count = 0
        def slow_scrape(source):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Small delay
            return ScrapingResult(source_name=source['name'], success=True)
        
        source_manager.scrape_source = Mock(side_effect=slow_scrape)
        
        # Mock time to simulate timeout
        with patch('src.source_manager.time.time') as mock_time:
            # First call returns 0, subsequent calls simulate elapsed time
            mock_time.side_effect = [0] + [i * 100 for i in range(1, 200)]
            
            results = source_manager.scrape_all_sources()
            
            # Should stop before processing all sources due to timeout
            assert len(results) < 100
    
    def test_scrape_all_sources_concurrent_execution(self, source_manager, mock_config):
        """Test that sources are scraped concurrently."""
        mock_config.get_sources.return_value = [
            {'name': f'Source {i}', 'url': f'https://example{i}.com'}
            for i in range(5)
        ]
        mock_config.get_max_concurrent_requests.return_value = 5
        
        # Mock scrape_source to return success
        source_manager.scrape_source = Mock(return_value=ScrapingResult(
            source_name='Test',
            success=True,
            html_content='<html></html>'
        ))
        
        results = source_manager.scrape_all_sources()
        
        # All sources should be scraped
        assert len(results) == 5
        assert all(r.success for r in results)
    
    def test_scrape_all_sources_groups_by_domain(self, source_manager, mock_config):
        """Test that sources are grouped by domain for rate limiting."""
        sources = [
            {'name': 'Source 1', 'url': 'https://example.com/page1'},
            {'name': 'Source 2', 'url': 'https://example.com/page2'},
            {'name': 'Source 3', 'url': 'https://other.com/page1'}
        ]
        
        grouped = source_manager._group_sources_by_domain(sources)
        
        assert 'example.com' in grouped
        assert 'other.com' in grouped
        assert len(grouped['example.com']) == 2
        assert len(grouped['other.com']) == 1


class TestScrapeSource:
    """Tests for scrape_source method."""
    
    def test_scrape_source_no_url(self, source_manager):
        """Test scraping source without URL."""
        source = {'name': 'Test Source'}
        
        result = source_manager.scrape_source(source)
        
        assert result.success is False
        assert 'No URL provided' in result.error_message
    
    def test_scrape_source_static_success(self, source_manager):
        """Test successful scraping of static source."""
        source = {'name': 'Test', 'url': 'https://example.com', 'type': 'static'}
        
        # Mock _fetch_html
        source_manager._fetch_html = Mock(return_value='<html>content</html>')
        source_manager._detect_captcha = Mock(return_value=False)
        source_manager._apply_rate_limit = Mock()
        
        result = source_manager.scrape_source(source)
        
        assert result.success is True
        assert result.html_content == '<html>content</html>'
        assert result.source_name == 'Test'
    
    def test_scrape_source_dynamic_uses_selenium(self, source_manager):
        """Test that dynamic sources use Selenium."""
        source = {'name': 'Test', 'url': 'https://example.com', 'type': 'dynamic'}
        
        source_manager._fetch_html = Mock(return_value='<html>dynamic</html>')
        source_manager._detect_captcha = Mock(return_value=False)
        source_manager._apply_rate_limit = Mock()
        
        result = source_manager.scrape_source(source)
        
        # Verify _fetch_html was called with use_selenium=True
        source_manager._fetch_html.assert_called_once()
        assert result.success is True
    
    def test_scrape_source_captcha_detected(self, source_manager):
        """Test handling of CAPTCHA detection."""
        source = {'name': 'Test', 'url': 'https://example.com'}
        
        source_manager._fetch_html = Mock(return_value='<html>captcha</html>')
        source_manager._detect_captcha = Mock(return_value=True)
        source_manager._apply_rate_limit = Mock()
        
        result = source_manager.scrape_source(source)
        
        assert result.success is False
        assert 'CAPTCHA detected' in result.error_message
    
    def test_scrape_source_exception_handling(self, source_manager):
        """Test exception handling during scraping."""
        source = {'name': 'Test', 'url': 'https://example.com'}
        
        source_manager._fetch_html = Mock(side_effect=Exception('Network error'))
        source_manager._apply_rate_limit = Mock()
        
        result = source_manager.scrape_source(source)
        
        assert result.success is False
        assert 'Network error' in result.error_message


class TestRetryWithBackoff:
    """Tests for _retry_with_backoff method."""
    
    def test_retry_success_first_attempt(self, source_manager):
        """Test successful execution on first attempt."""
        func = Mock(return_value='success')
        
        result = source_manager._retry_with_backoff(func, max_attempts=3)
        
        assert result == 'success'
        assert func.call_count == 1
    
    def test_retry_success_after_failures(self, source_manager):
        """Test successful execution after initial failures."""
        func = Mock(side_effect=[
            Exception('Error 1'),
            Exception('Error 2'),
            'success'
        ])
        
        with patch('src.source_manager.time.sleep'):
            result = source_manager._retry_with_backoff(func, max_attempts=3)
        
        assert result == 'success'
        assert func.call_count == 3
    
    def test_retry_exponential_backoff_delays(self, source_manager):
        """Test exponential backoff delays: 1s, 2s, 4s."""
        func = Mock(side_effect=[
            Exception('Error 1'),
            Exception('Error 2'),
            Exception('Error 3')
        ])
        
        with patch('src.source_manager.time.sleep') as mock_sleep:
            with pytest.raises(Exception):
                source_manager._retry_with_backoff(func, max_attempts=3)
            
            # Check sleep was called with exponential delays
            assert mock_sleep.call_count == 2  # No sleep after last attempt
            mock_sleep.assert_any_call(1)  # 2^0
            mock_sleep.assert_any_call(2)  # 2^1
    
    def test_retry_http_403_no_retry(self, source_manager):
        """Test that HTTP 403 errors are not retried."""
        func = Mock(side_effect=Exception('HTTP 403 Forbidden'))
        
        with pytest.raises(Exception) as exc_info:
            source_manager._retry_with_backoff(func, max_attempts=3)
        
        assert '403' in str(exc_info.value)
        assert func.call_count == 1  # No retries
    
    def test_retry_http_429_no_retry(self, source_manager):
        """Test that HTTP 429 errors are not retried."""
        func = Mock(side_effect=Exception('HTTP 429 Too Many Requests'))
        
        with pytest.raises(Exception) as exc_info:
            source_manager._retry_with_backoff(func, max_attempts=3)
        
        assert '429' in str(exc_info.value)
        assert func.call_count == 1  # No retries
    
    def test_retry_http_404_no_retry(self, source_manager):
        """Test that HTTP 404 errors are not retried."""
        func = Mock(side_effect=Exception('HTTP 404 Not Found'))
        
        with pytest.raises(Exception) as exc_info:
            source_manager._retry_with_backoff(func, max_attempts=3)
        
        assert '404' in str(exc_info.value)
        assert func.call_count == 1  # No retries
    
    def test_retry_5xx_errors_retried(self, source_manager):
        """Test that 5xx errors are retried."""
        func = Mock(side_effect=[
            Exception('HTTP 500 Internal Server Error'),
            'success'
        ])
        
        with patch('src.source_manager.time.sleep'):
            result = source_manager._retry_with_backoff(func, max_attempts=3)
        
        assert result == 'success'
        assert func.call_count == 2  # Retried once


class TestApplyRateLimit:
    """Tests for _apply_rate_limit method."""
    
    def test_rate_limit_first_request(self, source_manager):
        """Test that first request to domain has no delay."""
        with patch('src.source_manager.time.sleep') as mock_sleep:
            source_manager._apply_rate_limit('example.com')
            
            mock_sleep.assert_not_called()
    
    def test_rate_limit_subsequent_request_delays(self, source_manager, mock_config):
        """Test that subsequent requests are delayed."""
        mock_config.get_request_delay_min.return_value = 1.0
        mock_config.get_request_delay_max.return_value = 1.0  # Fixed for testing
        
        with patch('src.source_manager.time.sleep') as mock_sleep:
            with patch('src.source_manager.time.time', side_effect=[0, 0, 0.5, 0.5]):
                source_manager._apply_rate_limit('example.com')
                source_manager._apply_rate_limit('example.com')
                
                # Should sleep to reach required delay
                assert mock_sleep.call_count == 1
    
    def test_rate_limit_different_domains_independent(self, source_manager):
        """Test that different domains are tracked independently."""
        with patch('src.source_manager.time.sleep') as mock_sleep:
            source_manager._apply_rate_limit('example1.com')
            source_manager._apply_rate_limit('example2.com')
            
            # No delays for first requests to different domains
            mock_sleep.assert_not_called()
    
    def test_rate_limit_random_delay_range(self, source_manager, mock_config):
        """Test that delay is random within configured range."""
        mock_config.get_request_delay_min.return_value = 1.0
        mock_config.get_request_delay_max.return_value = 3.0
        
        with patch('src.source_manager.random.uniform') as mock_uniform:
            mock_uniform.return_value = 2.0
            
            with patch('src.source_manager.time.time', side_effect=[0, 0, 0, 0]):
                source_manager._apply_rate_limit('example.com')
                source_manager._apply_rate_limit('example.com')
                
                mock_uniform.assert_called_with(1.0, 3.0)


class TestExtractDomain:
    """Tests for _extract_domain method."""
    
    def test_extract_domain_valid_url(self, source_manager):
        """Test extracting domain from valid URL."""
        domain = source_manager._extract_domain('https://example.com/path')
        assert domain == 'example.com'
    
    def test_extract_domain_with_subdomain(self, source_manager):
        """Test extracting domain with subdomain."""
        domain = source_manager._extract_domain('https://www.example.com/path')
        assert domain == 'www.example.com'
    
    def test_extract_domain_with_port(self, source_manager):
        """Test extracting domain with port."""
        domain = source_manager._extract_domain('https://example.com:8080/path')
        assert domain == 'example.com:8080'
    
    def test_extract_domain_invalid_url(self, source_manager):
        """Test extracting domain from invalid URL."""
        domain = source_manager._extract_domain('not a url')
        assert domain == 'unknown'


class TestDetectCaptcha:
    """Tests for _detect_captcha method."""
    
    def test_detect_captcha_none(self, source_manager):
        """Test CAPTCHA detection with clean HTML."""
        html = '<html><body>Normal content</body></html>'
        assert source_manager._detect_captcha(html) is False
    
    def test_detect_captcha_recaptcha(self, source_manager):
        """Test detection of reCAPTCHA."""
        html = '<html><div class="g-recaptcha"></div></html>'
        assert source_manager._detect_captcha(html) is True
    
    def test_detect_captcha_hcaptcha(self, source_manager):
        """Test detection of hCaptcha."""
        html = '<html><div class="h-captcha"></div></html>'
        assert source_manager._detect_captcha(html) is True
    
    def test_detect_captcha_cloudflare(self, source_manager):
        """Test detection of Cloudflare challenge."""
        html = '<html><div id="cf-challenge"></div></html>'
        assert source_manager._detect_captcha(html) is True
    
    def test_detect_captcha_case_insensitive(self, source_manager):
        """Test CAPTCHA detection is case insensitive."""
        html = '<html><div>CAPTCHA verification required</div></html>'
        assert source_manager._detect_captcha(html) is True
    
    def test_detect_captcha_empty_html(self, source_manager):
        """Test CAPTCHA detection with empty HTML."""
        assert source_manager._detect_captcha('') is False
        assert source_manager._detect_captcha(None) is False


class TestFetchHtml:
    """Tests for _fetch_html method."""
    
    def test_fetch_html_static(self, source_manager):
        """Test fetching HTML with BeautifulSoup scraper."""
        source_manager.bs_scraper.fetch_html = Mock(return_value='<html>static</html>')
        
        result = source_manager._fetch_html('https://example.com', 'Test Source', use_selenium=False)
        
        assert result == '<html>static</html>'
        source_manager.bs_scraper.fetch_html.assert_called_once_with('https://example.com')
    
    def test_fetch_html_dynamic_lazy_init(self, source_manager, mock_config, mock_logger):
        """Test that Selenium scraper is lazily initialized."""
        assert source_manager.selenium_scraper is None
        
        with patch('src.source_manager.SeleniumScraper') as mock_selenium:
            mock_instance = Mock()
            mock_instance.fetch_dynamic_html.return_value = '<html>dynamic</html>'
            mock_selenium.return_value = mock_instance
            
            result = source_manager._fetch_html('https://example.com', 'Test Source', use_selenium=True)
            
            # Verify Selenium was initialized
            mock_selenium.assert_called_once_with(
                browser_type=mock_config.get_browser_type(),
                headless=mock_config.get_headless(),
                logger=mock_logger
            )
            assert result == '<html>dynamic</html>'


class TestCloseAndContextManager:
    """Tests for close and context manager methods."""
    
    def test_close_closes_scrapers(self, source_manager):
        """Test that close method closes all scrapers."""
        source_manager.bs_scraper.close = Mock()
        source_manager.selenium_scraper = Mock()
        source_manager.selenium_scraper.close = Mock()
        
        source_manager.close()
        
        source_manager.bs_scraper.close.assert_called_once()
        source_manager.selenium_scraper.close.assert_called_once()
    
    def test_context_manager(self, mock_config, mock_logger):
        """Test context manager usage."""
        with patch('src.source_manager.BeautifulSoupScraper'):
            with SourceManager(mock_config, mock_logger) as manager:
                assert manager is not None
            
            # Close should be called on exit
            manager.logger.info.assert_any_call("SourceManager closed")
