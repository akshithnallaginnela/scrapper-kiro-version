"""Selenium-based scraper for dynamic JavaScript-rendered content."""

import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException
)


class SeleniumScraper:
    """Handles dynamic content scraping with Selenium."""
    
    def __init__(
        self, 
        browser_type: str = "chrome", 
        headless: bool = True, 
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Selenium WebDriver with appropriate options.
        
        Args:
            browser_type: Browser to use ('chrome' or 'firefox')
            headless: Whether to run browser in headless mode
            logger: Logger instance for logging scraping events
            
        Raises:
            WebDriverException: If browser initialization fails
        """
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.logger = logger or logging.getLogger(__name__)
        self.driver = None
        
        try:
            self._initialize_driver()
            self.logger.debug(
                f"SeleniumScraper initialized with browser={browser_type}, "
                f"headless={headless}"
            )
        except WebDriverException as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def _initialize_driver(self) -> None:
        """Initialize WebDriver with appropriate options."""
        if self.browser_type == "chrome":
            options = webdriver.ChromeOptions()
            
            if self.headless:
                options.add_argument("--headless")
            
            # Disable image and video loading for performance
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.media": 2
            }
            options.add_experimental_option("prefs", prefs)
            
            # Additional performance optimizations
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Set user agent
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
            
            self.driver = webdriver.Chrome(options=options)
            
        elif self.browser_type == "firefox":
            options = webdriver.FirefoxOptions()
            
            if self.headless:
                options.add_argument("--headless")
            
            # Disable image and video loading for performance
            options.set_preference("permissions.default.image", 2)
            options.set_preference("media.autoplay.default", 5)
            
            # Set user agent
            options.set_preference(
                "general.useragent.override",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) "
                "Gecko/20100101 Firefox/89.0"
            )
            
            self.driver = webdriver.Firefox(options=options)
            
        else:
            raise ValueError(
                f"Unsupported browser type: {self.browser_type}. "
                "Use 'chrome' or 'firefox'."
            )
        
        # Set page load timeout
        self.driver.set_page_load_timeout(30)
    
    def fetch_dynamic_html(
        self, 
        url: str, 
        wait_selector: Optional[str] = None,
        timeout: int = 30
    ) -> str:
        """
        Fetch HTML from JavaScript-rendered page.
        
        Args:
            url: URL to fetch HTML from
            wait_selector: Optional CSS selector to wait for before extracting HTML
            timeout: Page load timeout in seconds (default: 30)
            
        Returns:
            HTML content as string after JavaScript execution
            
        Raises:
            TimeoutException: If page fails to load within timeout
            WebDriverException: For browser-related errors
        """
        try:
            self.logger.debug(f"Fetching dynamic HTML from: {url}")
            
            # Navigate to URL
            self.driver.get(url)
            
            # Wait for specific element if selector provided
            if wait_selector:
                self.logger.debug(f"Waiting for element: {wait_selector}")
                self.wait_for_element(wait_selector, timeout=10)
            
            # Get page source after JavaScript execution
            html = self.driver.page_source
            
            self.logger.info(f"Successfully fetched dynamic HTML from {url}")
            
            return html
            
        except TimeoutException as e:
            self.logger.error(f"Timeout loading page {url}: {e}")
            raise
        
        except WebDriverException as e:
            self.logger.error(f"WebDriver error fetching {url}: {e}")
            raise
        
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}")
            raise
    
    def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """
        Wait for element to appear on page using explicit wait.
        
        Args:
            selector: CSS selector for element to wait for
            timeout: Maximum wait time in seconds (default: 10)
            
        Returns:
            True if element appears within timeout, False otherwise
            
        Note:
            Uses explicit wait with expected conditions for reliability.
        """
        try:
            self.logger.debug(
                f"Waiting for element '{selector}' (timeout: {timeout}s)"
            )
            
            # Use explicit wait with expected conditions
            wait = WebDriverWait(self.driver, timeout)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            self.logger.debug(f"Element '{selector}' found")
            return True
            
        except TimeoutException:
            self.logger.warning(
                f"Element '{selector}' not found within {timeout}s"
            )
            return False
        
        except NoSuchElementException:
            self.logger.warning(f"Element '{selector}' does not exist")
            return False
        
        except Exception as e:
            self.logger.warning(f"Error waiting for element '{selector}': {e}")
            return False
    
    def close(self) -> None:
        """Close browser and cleanup resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.debug("SeleniumScraper browser closed")
            except Exception as e:
                self.logger.warning(f"Error closing browser: {e}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures browser is closed."""
        self.close()
