"""Product extraction module for parsing HTML and extracting structured product data."""

import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Tag
from datetime import datetime

from src.models import ProductRecord


class ProductExtractor:
    """Extracts structured product data from HTML using CSS selectors."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize ProductExtractor with logger.
        
        Args:
            logger: Logger instance for logging extraction events
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("ProductExtractor initialized")
    
    def extract_products(
        self,
        soup: BeautifulSoup,
        source_name: str,
        selectors: Dict[str, str]
    ) -> List[ProductRecord]:
        """
        Extract products from parsed HTML using CSS selectors.
        
        Args:
            soup: BeautifulSoup object containing parsed HTML
            source_name: Name of the source platform
            selectors: Dictionary mapping field names to CSS selectors
                      Expected keys: 'container', 'name', 'price', 'link', 'image'
        
        Returns:
            List of ProductRecord objects extracted from HTML
            
        Note:
            - Handles missing elements gracefully with default values
            - Validates URLs before adding to ProductRecord
            - Uses UTF-8 text extraction
            - Logs warnings for missing elements
        """
        products = []
        
        try:
            # Get container selector
            container_selector = selectors.get('container', 'div')
            self.logger.debug(f"Using container selector: {container_selector}")
            
            # Find all product containers
            containers = soup.select(container_selector)
            
            if not containers:
                self.logger.warning(
                    f"No product containers found for source '{source_name}' "
                    f"using selector '{container_selector}'"
                )
                return products
            
            self.logger.info(
                f"Found {len(containers)} product containers in {source_name}"
            )
            
            # Extract data from each container
            for idx, container in enumerate(containers):
                try:
                    # Extract fields with defaults
                    name = self._extract_field(
                        container,
                        selectors.get('name', ''),
                        default="Not Available"
                    )
                    
                    # Skip product if name is not available (required field)
                    if name == "Not Available" or not name.strip():
                        self.logger.warning(
                            f"Skipping product {idx} from {source_name}: "
                            f"missing required field 'name'"
                        )
                        continue
                    
                    price = self._extract_field(
                        container,
                        selectors.get('price', ''),
                        default="Not Available"
                    )
                    
                    link = self._extract_field(
                        container,
                        selectors.get('link', ''),
                        default="Not Available",
                        attribute='href'
                    )
                    
                    # Validate URL
                    if link != "Not Available" and not self._validate_url(link):
                        self.logger.warning(
                            f"Invalid URL for product '{name}' from {source_name}: {link}"
                        )
                        link = "Not Available"
                    
                    image_url = self._extract_field(
                        container,
                        selectors.get('image', ''),
                        default="Not Available",
                        attribute='src'
                    )
                    
                    # Validate image URL
                    if image_url != "Not Available" and not self._validate_url(image_url):
                        self.logger.warning(
                            f"Invalid image URL for product '{name}' from {source_name}: {image_url}"
                        )
                        image_url = "Not Available"
                    
                    # Create ProductRecord
                    product = ProductRecord(
                        name=name.strip(),
                        price=price.strip(),
                        source=source_name,
                        link=link,
                        image_url=image_url,
                        timestamp=datetime.now(),
                        mentions=1,
                        sources_list=[source_name]
                    )
                    
                    products.append(product)
                    self.logger.debug(f"Extracted product: {name} from {source_name}")
                    
                except Exception as e:
                    self.logger.warning(
                        f"Error extracting product {idx} from {source_name}: {e}"
                    )
                    continue
            
            self.logger.info(
                f"Successfully extracted {len(products)} products from {source_name}"
            )
            
        except Exception as e:
            self.logger.error(
                f"Error during product extraction from {source_name}: {e}"
            )
        
        return products
    
    def _extract_field(
        self,
        element: Tag,
        selector: str,
        default: str = "Not Available",
        attribute: Optional[str] = None
    ) -> str:
        """
        Extract single field from element with fallback to default value.
        
        Args:
            element: BeautifulSoup Tag element to search within
            selector: CSS selector to locate the field
            default: Default value if field is not found (default: "Not Available")
            attribute: HTML attribute to extract (e.g., 'href', 'src')
                      If None, extracts text content
        
        Returns:
            Extracted field value or default if not found
            
        Note:
            - Handles missing elements gracefully
            - Extracts text with UTF-8 encoding
            - Strips whitespace from extracted values
        """
        try:
            if not selector:
                return default
            
            # Find element using CSS selector
            found_element = element.select_one(selector)
            
            if not found_element:
                self.logger.debug(
                    f"Element not found for selector '{selector}', using default: {default}"
                )
                return default
            
            # Extract attribute or text
            if attribute:
                value = found_element.get(attribute, default)
                if value == default:
                    self.logger.debug(
                        f"Attribute '{attribute}' not found for selector '{selector}', "
                        f"using default: {default}"
                    )
            else:
                # Extract text with UTF-8 encoding
                value = found_element.get_text(strip=True)
                if not value:
                    self.logger.debug(
                        f"Empty text for selector '{selector}', using default: {default}"
                    )
                    return default
            
            return str(value).strip() if value else default
            
        except Exception as e:
            self.logger.debug(
                f"Error extracting field with selector '{selector}': {e}, "
                f"using default: {default}"
            )
            return default
    
    def _validate_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL string to validate
        
        Returns:
            True if URL is properly formatted, False otherwise
            
        Note:
            - Checks for valid scheme (http, https)
            - Checks for valid domain
            - Handles edge cases (empty strings, None, malformed URLs)
        """
        try:
            if not url or not isinstance(url, str):
                return False
            
            # Parse URL
            parsed = urlparse(url)
            
            # Check for valid scheme and netloc (domain)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check for valid scheme (http or https)
            if parsed.scheme not in ['http', 'https']:
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"URL validation error for '{url}': {e}")
            return False
