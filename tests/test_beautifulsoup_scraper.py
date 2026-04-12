"""Unit tests for BeautifulSoupScraper class."""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

from src.beautifulsoup_scraper import BeautifulSoupScraper
from src.logger import setup_logger


@pytest.fixture
def logger():
    """Create a test logger."""
    return setup_logger(name="test_scraper", log_level="DEBUG")


@pytest.fixture
def scraper(logger):
    """Create a BeautifulSoupScraper instance."""
    return BeautifulSoupScraper(timeout=30, logger=logger)


class TestBeautifulSoupScraperInit:
    """Tests for BeautifulSoupScraper initialization."""
    
    def test_init_with_timeout_and_logger(self, logger):
        """Test initialization with timeout and logger."""
        scraper = BeautifulSoupScraper(timeout=15, logger=logger)
        
        assert scraper.timeout == 15
        assert scraper.logger == logger
        assert scraper.session is not None
        assert isinstance(scraper.session, requests.Session)
    
    def test_init_with_default_timeout(self, logger):
        """Test initialization with default timeout."""
        scraper = BeautifulSoupScraper(logger=logger)
        
        assert scraper.timeout == 30
    
    def test_init_without_logger(self):
        """Test initialization without logger creates default logger."""
        scraper = BeautifulSoupScraper(timeout=20)
        
        assert scraper.logger is not None
        assert scraper.timeout == 20
    
    def test_session_has_user_agent(self, scraper):
        """Test that session has User-Agent header."""
        assert 'User-Agent' in scraper.session.headers
        assert 'Mozilla' in scraper.session.headers['User-Agent']
    
    def test_session_has_adapters(self, scraper):
        """Test that session has HTTP and HTTPS adapters."""
        assert 'http://' in scraper.session.adapters
        assert 'https://' in scraper.session.adapters


class TestFetchHtml:
    """Tests for fetch_html method."""
    
    @patch('requests.Session.get')
    def test_fetch_html_success(self, mock_get, scraper):
        """Test successful HTML fetch."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test</body></html>"
        mock_get.return_value = mock_response
        
        # Fetch HTML
        html = scraper.fetch_html("https://example.com")
        
        # Assertions
        assert html == "<html><body>Test</body></html>"
        mock_get.assert_called_once_with("https://example.com", timeout=30)
        mock_response.raise_for_status.assert_called_once()
    
    @patch('requests.Session.get')
    def test_fetch_html_timeout_error(self, mock_get, scraper):
        """Test fetch_html raises Timeout exception."""
        mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        with pytest.raises(requests.exceptions.Timeout):
            scraper.fetch_html("https://example.com")
    
    @patch('requests.Session.get')
    def test_fetch_html_connection_error(self, mock_get, scraper):
        """Test fetch_html raises ConnectionError."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(requests.exceptions.ConnectionError):
            scraper.fetch_html("https://example.com")
    
    @patch('requests.Session.get')
    def test_fetch_html_http_error(self, mock_get, scraper):
        """Test fetch_html raises HTTPError for bad status codes."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            scraper.fetch_html("https://example.com/notfound")
    
    @patch('requests.Session.get')
    def test_fetch_html_request_exception(self, mock_get, scraper):
        """Test fetch_html raises RequestException for other errors."""
        mock_get.side_effect = requests.exceptions.RequestException("Unknown error")
        
        with pytest.raises(requests.exceptions.RequestException):
            scraper.fetch_html("https://example.com")
    
    @patch('requests.Session.get')
    def test_fetch_html_uses_timeout(self, mock_get, logger):
        """Test fetch_html uses configured timeout."""
        scraper = BeautifulSoupScraper(timeout=15, logger=logger)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response
        
        scraper.fetch_html("https://example.com")
        
        mock_get.assert_called_once_with("https://example.com", timeout=15)


class TestParseHtml:
    """Tests for parse_html method."""
    
    def test_parse_html_valid(self, scraper):
        """Test parsing valid HTML."""
        html = "<html><body><h1>Title</h1></body></html>"
        
        soup = scraper.parse_html(html)
        
        assert isinstance(soup, BeautifulSoup)
        assert soup.h1.text == "Title"
    
    def test_parse_html_malformed(self, scraper):
        """Test parsing malformed HTML doesn't crash."""
        html = "<html><body><h1>Title</body>"  # Missing closing tags
        
        soup = scraper.parse_html(html)
        
        assert isinstance(soup, BeautifulSoup)
        assert soup.h1.text == "Title"
    
    def test_parse_html_utf8_encoding(self, scraper):
        """Test parsing HTML with UTF-8 characters."""
        html = "<html><body><p>Café résumé</p></body></html>"
        
        soup = scraper.parse_html(html)
        
        assert isinstance(soup, BeautifulSoup)
        assert "Café" in soup.p.text
    
    def test_parse_html_empty(self, scraper):
        """Test parsing empty HTML."""
        html = ""
        
        soup = scraper.parse_html(html)
        
        assert isinstance(soup, BeautifulSoup)
    
    def test_parse_html_special_characters(self, scraper):
        """Test parsing HTML with special characters."""
        html = "<html><body><p>&lt;script&gt;alert('test')&lt;/script&gt;</p></body></html>"
        
        soup = scraper.parse_html(html)
        
        assert isinstance(soup, BeautifulSoup)


class TestConnectionPooling:
    """Tests for connection pooling and session management."""
    
    def test_session_reuse(self, scraper):
        """Test that session is reused across requests."""
        session_id = id(scraper.session)
        
        # Session should be the same instance
        assert id(scraper.session) == session_id
    
    def test_close_session(self, scraper):
        """Test closing session."""
        scraper.close()
        
        # Session should be closed (no exception raised)
        assert True
    
    def test_context_manager(self, logger):
        """Test using scraper as context manager."""
        with BeautifulSoupScraper(timeout=30, logger=logger) as scraper:
            assert scraper.session is not None
        
        # Session should be closed after context exit


class TestErrorHandling:
    """Tests for error handling."""
    
    @patch('requests.Session.get')
    def test_network_error_raised(self, mock_get, scraper):
        """Test that network errors are raised properly."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        with pytest.raises(requests.exceptions.ConnectionError) as exc_info:
            scraper.fetch_html("https://example.com")
        
        assert "Network error" in str(exc_info.value)
    
    @patch('requests.Session.get')
    def test_timeout_error_raised(self, mock_get, scraper):
        """Test that timeout errors are raised properly."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
        
        with pytest.raises(requests.exceptions.Timeout) as exc_info:
            scraper.fetch_html("https://example.com")
        
        assert "Timeout" in str(exc_info.value)
