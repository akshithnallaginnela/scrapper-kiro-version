"""Source management for coordinating scraping from multiple sources."""

import logging
import time
import random
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict, Any, Callable, Optional
from datetime import datetime
from urllib.parse import urlparse

from src.models import ScrapingResult
from src.beautifulsoup_scraper import BeautifulSoupScraper
from src.selenium_scraper import SeleniumScraper
from src.cache_manager import CacheManager


class SourceManager:
    """Manages connections and requests to data sources."""
    
    def __init__(self, config, logger: logging.Logger):
        """
        Initialize with configuration and logger.
        
        Args:
            config: ConfigurationManager instance
            logger: Logger instance for logging scraping events
        """
        self.config = config
        self.logger = logger
        
        # Track last request time per domain for rate limiting
        self._domain_last_request: Dict[str, float] = {}
        
        # Initialize scrapers
        self.bs_scraper = BeautifulSoupScraper(
            timeout=config.get_timeout(),
            logger=logger
        )
        
        self.selenium_scraper = None  # Lazy initialization
        
        # Initialize cache manager for test mode
        self.test_mode = config.get_test_mode()
        self.cache_manager = None
        if self.test_mode:
            self.cache_manager = CacheManager(
                cache_directory=config.get_test_data_directory(),
                logger=logger
            )
            self.logger.info("Test mode enabled - using cached responses")
        
        self.logger.info("SourceManager initialized")
    
    def scrape_all_sources(self) -> List[ScrapingResult]:
        """
        Scrape all configured sources with concurrent requests and timeout handling.
        
        Returns:
            List of ScrapingResult objects containing scraping outcomes
            
        Note:
            Implements 300-second total timeout as per requirement 1.7.
            Uses concurrent requests for different domains (requirement 12.1).
            Continues scraping remaining sources if individual sources fail.
        """
        sources = self.config.get_sources()
        results: List[ScrapingResult] = []
        
        if not sources:
            self.logger.warning("No sources configured for scraping")
            return results
        
        self.logger.info(f"Starting concurrent scraping of {len(sources)} sources")
        start_time = time.time()
        total_timeout = 300  # 300 seconds as per requirement 1.7
        
        # Group sources by domain for rate limiting
        sources_by_domain = self._group_sources_by_domain(sources)
        
        # Use ThreadPoolExecutor for concurrent scraping
        max_workers = min(self.config.get_max_concurrent_requests(), len(sources))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scraping tasks
            future_to_source = {
                executor.submit(self.scrape_source, source): source
                for source in sources
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_source, timeout=total_timeout):
                # Check if total timeout exceeded
                elapsed = time.time() - start_time
                if elapsed >= total_timeout:
                    self.logger.warning(
                        f"Total timeout of {total_timeout}s exceeded. "
                        f"Stopping scraping. Elapsed: {elapsed:.2f}s"
                    )
                    # Cancel remaining futures
                    for f in future_to_source:
                        f.cancel()
                    break
                
                try:
                    result = future.result(timeout=1)
                    results.append(result)
                    
                    # Log result
                    if result.success:
                        self.logger.info(
                            f"Successfully scraped {result.source_name} "
                            f"in {result.response_time:.2f}s"
                        )
                    else:
                        self.logger.warning(
                            f"Failed to scrape {result.source_name}: "
                            f"{result.error_message}"
                        )
                except Exception as e:
                    source = future_to_source[future]
                    source_name = source.get('name', 'Unknown')
                    self.logger.error(f"Exception scraping {source_name}: {e}")
                    results.append(ScrapingResult(
                        source_name=source_name,
                        success=False,
                        error_message=str(e)
                    ))
        
        total_elapsed = time.time() - start_time
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        self.logger.info(
            f"Concurrent scraping completed in {total_elapsed:.2f}s. "
            f"Successful: {successful}, Failed: {failed}"
        )
        
        return results
    
    def _group_sources_by_domain(self, sources: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group sources by domain for rate limiting coordination.
        
        Args:
            sources: List of source configurations
            
        Returns:
            Dictionary mapping domain to list of sources
        """
        grouped = {}
        for source in sources:
            url = source.get('url', '')
            domain = self._extract_domain(url)
            if domain not in grouped:
                grouped[domain] = []
            grouped[domain].append(source)
        return grouped
    
    def scrape_source(self, source: Dict[str, Any]) -> ScrapingResult:
        """
        Scrape single source with retry logic and error handling.
        
        Args:
            source: Dictionary containing source configuration
                   Expected keys: 'name', 'url', 'type' (optional)
        
        Returns:
            ScrapingResult object with scraping outcome
            
        Note:
            Implements retry logic with exponential backoff (requirement 6.1).
            Handles HTTP status codes 403, 429, 404, 5xx (requirement 6.2).
            Detects CAPTCHA (requirement 6.6).
        """
        source_name = source.get('name', 'Unknown')
        url = source.get('url', '')
        source_type = source.get('type', 'static')  # 'static' or 'dynamic'
        
        if not url:
            return ScrapingResult(
                source_name=source_name,
                success=False,
                error_message="No URL provided for source"
            )
        
        self.logger.debug(f"Scraping source: {source_name} ({url})")
        
        start_time = time.time()
        
        # Apply rate limiting
        domain = self._extract_domain(url)
        self._apply_rate_limit(domain)
        
        # Determine scraper type
        use_selenium = source_type.lower() == 'dynamic'
        
        # Scrape with retry logic
        try:
            html_content = self._retry_with_backoff(
                func=lambda: self._fetch_html(url, source_name, use_selenium),
                max_attempts=self.config.get_retry_attempts()
            )
            
            # Check for CAPTCHA
            if self._detect_captcha(html_content):
                self.logger.warning(f"CAPTCHA detected on {source_name}")
                return ScrapingResult(
                    source_name=source_name,
                    success=False,
                    error_message="CAPTCHA detected",
                    response_time=time.time() - start_time
                )
            
            response_time = time.time() - start_time
            
            return ScrapingResult(
                source_name=source_name,
                success=True,
                html_content=html_content,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            
            self.logger.error(
                f"Failed to scrape {source_name} after retries: {error_msg}"
            )
            
            return ScrapingResult(
                source_name=source_name,
                success=False,
                error_message=error_msg,
                response_time=response_time
            )
    
    def _retry_with_backoff(
        self, 
        func: Callable, 
        max_attempts: int
    ) -> Any:
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            max_attempts: Maximum number of retry attempts
            
        Returns:
            Result of successful function execution
            
        Raises:
            Exception: Last exception if all attempts fail
            
        Note:
            Implements exponential backoff: 1s, 2s, 4s delays.
            Handles HTTP 403, 429 by skipping without retry (requirement 6.2).
        """
        last_exception = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                self.logger.debug(f"Attempt {attempt}/{max_attempts}")
                result = func()
                return result
                
            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()
                
                # Check for HTTP status codes that should not be retried
                if '403' in error_msg or 'forbidden' in error_msg:
                    self.logger.warning("HTTP 403 Forbidden - skipping source")
                    raise
                
                if '429' in error_msg or 'too many requests' in error_msg:
                    self.logger.warning("HTTP 429 Too Many Requests - skipping source")
                    raise
                
                if '404' in error_msg or 'not found' in error_msg:
                    self.logger.warning("HTTP 404 Not Found - skipping source")
                    raise
                
                # For other errors, retry with exponential backoff
                if attempt < max_attempts:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = 2 ** (attempt - 1)
                    self.logger.warning(
                        f"Attempt {attempt} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(
                        f"All {max_attempts} attempts failed. Last error: {e}"
                    )
        
        # All attempts failed
        raise last_exception
    
    def _apply_rate_limit(self, domain: str) -> None:
        """
        Apply rate limiting delay for domain.
        
        Args:
            domain: Domain name to apply rate limiting for
            
        Note:
            Implements random delays of 1-3 seconds between requests
            to the same domain (requirement 6.5).
        """
        if domain in self._domain_last_request:
            last_request_time = self._domain_last_request[domain]
            elapsed = time.time() - last_request_time
            
            # Random delay between min and max
            min_delay = self.config.get_request_delay_min()
            max_delay = self.config.get_request_delay_max()
            required_delay = random.uniform(min_delay, max_delay)
            
            if elapsed < required_delay:
                sleep_time = required_delay - elapsed
                self.logger.debug(
                    f"Rate limiting: sleeping {sleep_time:.2f}s for {domain}"
                )
                time.sleep(sleep_time)
        
        # Update last request time
        self._domain_last_request[domain] = time.time()
    
    def _fetch_html(self, url: str, source_name: str, use_selenium: bool) -> str:
        """
        Fetch HTML using appropriate scraper or from cache in test mode.
        
        Args:
            url: URL to fetch
            source_name: Name of the source (for cache lookup)
            use_selenium: Whether to use Selenium (True) or BeautifulSoup (False)
            
        Returns:
            HTML content as string
            
        Raises:
            Exception: If fetching fails
        """
        # In test mode, try to load from cache first
        if self.test_mode and self.cache_manager:
            cached_html = self.cache_manager.get_cached_html(url, source_name)
            
            if cached_html:
                self.logger.info(f"Using cached response for {source_name}")
                return cached_html
            else:
                self.logger.warning(
                    f"No cached response found for {url} in test mode. "
                    "Falling back to live request."
                )
        
        # Live request (normal mode or cache miss)
        if use_selenium:
            # Lazy initialize Selenium scraper
            if self.selenium_scraper is None:
                self.selenium_scraper = SeleniumScraper(
                    browser_type=self.config.get_browser_type(),
                    headless=self.config.get_headless(),
                    logger=self.logger
                )
            
            return self.selenium_scraper.fetch_dynamic_html(url)
        else:
            return self.bs_scraper.fetch_html(url)
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL for rate limiting tracking.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain name (e.g., 'example.com')
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc or 'unknown'
        except Exception:
            return 'unknown'
    
    def _detect_captcha(self, html_content: str) -> bool:
        """
        Detect CAPTCHA in HTML content.
        
        Args:
            html_content: HTML content to check
            
        Returns:
            True if CAPTCHA detected, False otherwise
            
        Note:
            Checks for common CAPTCHA indicators in HTML.
        """
        if not html_content:
            return False
        
        html_lower = html_content.lower()
        
        # Common CAPTCHA indicators
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'g-recaptcha',
            'hcaptcha',
            'h-captcha',
            'challenge-form',
            'cf-challenge',  # Cloudflare
            'security check',
            'verify you are human'
        ]
        
        for indicator in captcha_indicators:
            if indicator in html_lower:
                return True
        
        return False
    
    def close(self) -> None:
        """Close all scrapers and cleanup resources."""
        try:
            if self.bs_scraper:
                self.bs_scraper.close()
            
            if self.selenium_scraper:
                self.selenium_scraper.close()
            
            self.logger.info("SourceManager closed")
        except Exception as e:
            self.logger.warning(f"Error closing SourceManager: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()
