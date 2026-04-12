"""Data models for the Organic Products Web Scraper."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class ProductRecord:
    """Represents a single product with extracted information."""
    
    name: str
    price: str  # String to handle "Not Available" and currency symbols
    source: str
    link: str
    image_url: str
    timestamp: datetime
    mentions: int = 1  # Number of times product appears across sources
    sources_list: List[str] = field(default_factory=list)  # All sources mentioning product
    
    def __post_init__(self):
        """Validate required fields after initialization."""
        if not self.name:
            raise ValueError("Product name is required")
        if not self.source:
            raise ValueError("Product source is required")


@dataclass
class ScrapingResult:
    """Represents the result of a scraping operation."""
    
    source_name: str
    success: bool
    html_content: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    response_time: float = 0.0  # Seconds


@dataclass
class TrendingScore:
    """Represents a product's trending score components."""
    
    product: 'ProductRecord'
    frequency_score: float  # Based on mention count
    recency_score: float    # Based on timestamp recency
    diversity_score: float  # Based on source diversity
    total_score: float = 0.0  # Weighted combination
    
    def calculate_total(
        self, 
        frequency_weight: float = 0.4,
        recency_weight: float = 0.4,
        diversity_weight: float = 0.2
    ) -> float:
        """Calculate weighted total score."""
        self.total_score = (
            self.frequency_score * frequency_weight +
            self.recency_score * recency_weight +
            self.diversity_score * diversity_weight
        )
        return self.total_score


@dataclass
class ScraperConfiguration:
    """Application configuration settings."""
    
    sources: List[Dict[str, str]]  # List of {name, url, type, selectors}
    timeout: int = 30
    retry_attempts: int = 3
    output_directory: str = "./output"
    browser_type: str = "chrome"
    headless: bool = True
    request_delay_min: float = 1.0
    request_delay_max: float = 3.0
    max_concurrent_requests: int = 5
    log_level: str = "INFO"
    log_file: str = "scraper.log"
    max_log_size_mb: int = 10
    test_mode: bool = False
    test_data_directory: str = "./test_data"


@dataclass
class OutputMetadata:
    """Metadata included in output files."""
    
    collection_timestamp: datetime
    total_sources_configured: int
    sources_successfully_scraped: List[str]
    sources_failed: List[str]
    total_products_found: int
    top_products_count: int
    scraping_duration_seconds: float
    version: str = "1.0.0"
