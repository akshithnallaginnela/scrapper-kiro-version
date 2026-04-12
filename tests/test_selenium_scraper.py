"""Unit tests for SeleniumScraper class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException
)
from src.selenium_scraper import SeleniumScraper
from src.logger import setup_logger


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    return setup_logger(name="test_selenium", log_level="DEBUG")


@pytest.fixture
def mock_chrome_driver():
    """Create a mock Chrome WebDriver."""
    with patch('src.selenium_scraper.webdriver.Chrome') as mock_chrome:
        driver = MagicMock()
        mock_chrome.return_value = driver
        yield driver


@pytest.fixture
def mock_firefox_driver():
    """Create a mock Firefox WebDriver."""
    with patch('src.selenium_scraper.webdriver.Firefox') as mock_firefox:
        driver = MagicMock()
        mock_firefox.return_value = driver
        yield driver


class TestSeleniumScraperInit:
    """Test SeleniumScraper initialization."""
    
    def test_init_chrome_headless(self, mock_chrome_driver, mock_logger):
        """Test initialization with Chrome in headless mode."""
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        assert scraper.browser_type == "chrome"
        assert scraper.headless is True
        assert scraper.driver is not None
    
    def test_init_chrome_non_headless(self, mock_chrome_driver, mock_logger):
        """Test initialization with Chrome in non-headless mode."""
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=False,
            logger=mock_logger
        )
        
        assert scraper.headless is False
        assert scraper.driver is not None
    
    def test_init_firefox_headless(self, mock_firefox_driver, mock_logger):
        """Test initialization with Firefox in headless mode."""
        scraper = SeleniumScraper(
            browser_type="firefox",
            headless=True,
            logger=mock_logger
        )
        
        assert scraper.browser_type == "firefox"
        assert scraper.headless is True
        assert scraper.driver is not None
    
    def test_init_unsupported_browser(self, mock_logger):
        """Test initialization with unsupported browser type."""
        with pytest.raises(ValueError, match="Unsupported browser type"):
            SeleniumScraper(
                browser_type="safari",
                headless=True,
                logger=mock_logger
            )
    
    def test_init_webdriver_exception(self, mock_logger):
        """Test initialization when WebDriver fails."""
        with patch('src.selenium_scraper.webdriver.Chrome') as mock_chrome:
            mock_chrome.side_effect = WebDriverException("Driver not found")
            
            with pytest.raises(WebDriverException):
                SeleniumScraper(
                    browser_type="chrome",
                    headless=True,
                    logger=mock_logger
                )
    
    def test_init_default_logger(self, mock_chrome_driver):
        """Test initialization with default logger."""
        scraper = SeleniumScraper(browser_type="chrome")
        
        assert scraper.logger is not None
        assert scraper.driver is not None


class TestSeleniumScraperFetchDynamicHTML:
    """Test fetch_dynamic_html method."""
    
    def test_fetch_dynamic_html_success(self, mock_chrome_driver, mock_logger):
        """Test successful HTML fetching."""
        mock_chrome_driver.page_source = "<html><body>Test Content</body></html>"
        
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        html = scraper.fetch_dynamic_html("https://example.com")
        
        assert html == "<html><body>Test Content</body></html>"
        mock_chrome_driver.get.assert_called_once_with("https://example.com")
    
    def test_fetch_dynamic_html_with_wait_selector(
        self, 
        mock_chrome_driver, 
        mock_logger
    ):
        """Test HTML fetching with wait selector."""
        mock_chrome_driver.page_source = "<html><body>Test Content</body></html>"
        
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        with patch.object(scraper, 'wait_for_element', return_value=True):
            html = scraper.fetch_dynamic_html(
                "https://example.com",
                wait_selector=".product"
            )
        
        assert html == "<html><body>Test Content</body></html>"
        mock_chrome_driver.get.assert_called_once_with("https://example.com")
    
    def test_fetch_dynamic_html_timeout(self, mock_chrome_driver, mock_logger):
        """Test HTML fetching with timeout exception."""
        mock_chrome_driver.get.side_effect = TimeoutException("Page load timeout")
        
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        with pytest.raises(TimeoutException):
            scraper.fetch_dynamic_html("https://example.com")
    
    def test_fetch_dynamic_html_webdriver_exception(
        self, 
        mock_chrome_driver, 
        mock_logger
    ):
        """Test HTML fetching with WebDriver exception."""
        mock_chrome_driver.get.side_effect = WebDriverException("Browser crashed")
        
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        with pytest.raises(WebDriverException):
            scraper.fetch_dynamic_html("https://example.com")


class TestSeleniumScraperWaitForElement:
    """Test wait_for_element method."""
    
    def test_wait_for_element_success(self, mock_chrome_driver, mock_logger):
        """Test successful element wait."""
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        with patch('src.selenium_scraper.WebDriverWait') as mock_wait:
            mock_wait_instance = MagicMock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.return_value = True
            
            result = scraper.wait_for_element(".product", timeout=10)
        
        assert result is True
    
    def test_wait_for_element_timeout(self, mock_chrome_driver, mock_logger):
        """Test element wait with timeout."""
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        with patch('src.selenium_scraper.WebDriverWait') as mock_wait:
            mock_wait_instance = MagicMock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.side_effect = TimeoutException("Element not found")
            
            result = scraper.wait_for_element(".product", timeout=10)
        
        assert result is False
    
    def test_wait_for_element_no_such_element(
        self, 
        mock_chrome_driver, 
        mock_logger
    ):
        """Test element wait with NoSuchElementException."""
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        with patch('src.selenium_scraper.WebDriverWait') as mock_wait:
            mock_wait_instance = MagicMock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.side_effect = NoSuchElementException(
                "Element does not exist"
            )
            
            result = scraper.wait_for_element(".product", timeout=10)
        
        assert result is False
    
    def test_wait_for_element_custom_timeout(
        self, 
        mock_chrome_driver, 
        mock_logger
    ):
        """Test element wait with custom timeout."""
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        with patch('src.selenium_scraper.WebDriverWait') as mock_wait:
            mock_wait_instance = MagicMock()
            mock_wait.return_value = mock_wait_instance
            mock_wait_instance.until.return_value = True
            
            result = scraper.wait_for_element(".product", timeout=5)
        
        assert result is True
        mock_wait.assert_called_once_with(scraper.driver, 5)


class TestSeleniumScraperClose:
    """Test close method."""
    
    def test_close_success(self, mock_chrome_driver, mock_logger):
        """Test successful browser close."""
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        scraper.close()
        
        mock_chrome_driver.quit.assert_called_once()
        assert scraper.driver is None
    
    def test_close_with_exception(self, mock_chrome_driver, mock_logger):
        """Test browser close with exception."""
        mock_chrome_driver.quit.side_effect = Exception("Close error")
        
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        # Should not raise exception
        scraper.close()
        
        assert scraper.driver is None
    
    def test_close_when_driver_none(self, mock_chrome_driver, mock_logger):
        """Test close when driver is already None."""
        scraper = SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        )
        
        scraper.driver = None
        scraper.close()  # Should not raise exception


class TestSeleniumScraperContextManager:
    """Test context manager functionality."""
    
    def test_context_manager_success(self, mock_chrome_driver, mock_logger):
        """Test context manager with successful execution."""
        with SeleniumScraper(
            browser_type="chrome",
            headless=True,
            logger=mock_logger
        ) as scraper:
            assert scraper.driver is not None
        
        # Browser should be closed after context exit
        mock_chrome_driver.quit.assert_called_once()
    
    def test_context_manager_with_exception(
        self, 
        mock_chrome_driver, 
        mock_logger
    ):
        """Test context manager with exception during execution."""
        try:
            with SeleniumScraper(
                browser_type="chrome",
                headless=True,
                logger=mock_logger
            ) as scraper:
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Browser should still be closed after exception
        mock_chrome_driver.quit.assert_called_once()
