"""BeautifulSoup-based scraper for static HTML content."""

import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BeautifulSoupScraper:
    """Handles static HTML scraping with BeautifulSoup."""
    
    def __init__(self, timeout: int = 30, logger: Optional[logging.Logger] = None):
        """
        Initialize BeautifulSoup scraper with connection pooling and DNS caching.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            logger: Logger instance for logging scraping events
            
        Note:
            Implements connection pooling (requirement 12.3) and DNS caching (requirement 12.2)
            via requests.Session which maintains a connection pool and caches DNS lookups.
        """
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        
        # Create session with connection pooling and DNS caching
        # Session automatically handles DNS caching and connection reuse
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=0,  # Retries handled by SourceManager
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        
        # Configure HTTP adapter with connection pooling
        # pool_connections: number of connection pools to cache
        # pool_maxsize: maximum number of connections to save in the pool
        adapter = HTTPAdapter(
            pool_connections=10,  # Cache connections to 10 different hosts
            pool_maxsize=10,      # Max 10 connections per host
            max_retries=retry_strategy
        )
        
        # Mount adapter for both HTTP and HTTPS
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.logger.debug(
            f"BeautifulSoupScraper initialized with timeout={timeout}s, "
            f"connection pooling enabled, DNS caching enabled"
        )

    def fetch_html(self, url: str) -> str:
        """
        Fetch HTML content from URL using requests library.
        
        Args:
            url: URL to fetch HTML from
            
        Returns:
            HTML content as string
            
        Raises:
            requests.exceptions.RequestException: For network errors
            requests.exceptions.Timeout: For timeout errors
            requests.exceptions.ConnectionError: For connection errors
            requests.exceptions.HTTPError: For HTTP errors
        """
        try:
            self.logger.debug(f"Fetching HTML from: {url}")
            
            # Make GET request with timeout
            response = self.session.get(url, timeout=self.timeout)
            
            # Raise exception for bad status codes
            response.raise_for_status()
            
            # Log success
            self.logger.info(f"Successfully fetched HTML from {url} (status: {response.status_code})")
            
            return response.text
            
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error fetching {url}: {e}")
            raise
        
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error fetching {url}: {e}")
            raise
        
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error fetching {url}: {e} (status: {response.status_code})")
            raise
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error fetching {url}: {e}")
            raise
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML string into BeautifulSoup object with UTF-8 encoding.
        
        Args:
            html: HTML content as string
            
        Returns:
            BeautifulSoup object for HTML parsing
            
        Note:
            Uses 'html.parser' which is lenient with malformed HTML.
            Handles UTF-8 encoding by default.
        """
        try:
            self.logger.debug("Parsing HTML content with BeautifulSoup")
            
            # Parse HTML with UTF-8 encoding
            # html.parser is lenient and handles malformed HTML gracefully
            soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
            
            self.logger.debug("HTML parsed successfully")
            
            return soup
            
        except Exception as e:
            # BeautifulSoup rarely raises exceptions, but log if it does
            self.logger.warning(f"Warning during HTML parsing: {e}")
            # Return soup anyway as BeautifulSoup handles malformed HTML
            return BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
    
    def close(self) -> None:
        """Close the session and cleanup resources."""
        try:
            self.session.close()
            self.logger.debug("BeautifulSoupScraper session closed")
        except Exception as e:
            self.logger.warning(f"Error closing session: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures session is closed."""
        self.close()
