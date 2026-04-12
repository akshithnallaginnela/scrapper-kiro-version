"""Data aggregation and normalization for the Organic Products Web Scraper."""

import logging
from typing import List, Dict
from difflib import SequenceMatcher
from src.models import ProductRecord


class DataAggregator:
    """Aggregates and normalizes product data from multiple sources."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize with logger.
        
        Args:
            logger: Logger instance for recording aggregation activities
        """
        self.logger = logger
        self.logger.info("DataAggregator initialized")
    
    def aggregate(
        self, 
        products_by_source: Dict[str, List[ProductRecord]]
    ) -> List[ProductRecord]:
        """
        Combine products from all sources.
        Handles deduplication and normalization.
        
        Args:
            products_by_source: Dictionary mapping source names to lists of ProductRecords
            
        Returns:
            List of aggregated and deduplicated ProductRecords
        """
        self.logger.info(f"Starting aggregation from {len(products_by_source)} sources")
        
        # Flatten all products into a single list
        all_products = []
        for source_name, products in products_by_source.items():
            self.logger.debug(f"Processing {len(products)} products from {source_name}")
            all_products.extend(products)
        
        self.logger.info(f"Total products before deduplication: {len(all_products)}")
        
        # Normalize all products
        normalized_products = [self._normalize_product(p) for p in all_products]
        
        # Deduplicate products
        deduplicated_products = self._deduplicate(normalized_products)
        
        self.logger.info(f"Total products after deduplication: {len(deduplicated_products)}")
        
        return deduplicated_products

    def _deduplicate(self, products: List[ProductRecord]) -> List[ProductRecord]:
        """
        Remove duplicate products based on name similarity.
        
        Uses fuzzy string matching to identify products with similar names
        (e.g., "Organic Honey" and "organic honey " are considered duplicates).
        When duplicates are found, merges them by:
        - Keeping the most complete product record
        - Incrementing the mentions count
        - Tracking all sources that mentioned the product
        
        Args:
            products: List of ProductRecords to deduplicate
            
        Returns:
            List of deduplicated ProductRecords with updated mentions and sources
        """
        if not products:
            return []
        
        deduplicated = []
        similarity_threshold = 0.85  # 85% similarity threshold for matching
        
        for product in products:
            # Find if this product is similar to any already processed product
            matched = False
            
            for existing in deduplicated:
                similarity = self._calculate_similarity(
                    product.name.lower(), 
                    existing.name.lower()
                )
                
                if similarity >= similarity_threshold:
                    # Found a duplicate - merge the products
                    self.logger.debug(
                        f"Merging duplicate: '{product.name}' with '{existing.name}' "
                        f"(similarity: {similarity:.2f})"
                    )
                    
                    # Increment mentions count
                    existing.mentions += 1
                    
                    # Add source to sources_list if not already present
                    if product.source not in existing.sources_list:
                        existing.sources_list.append(product.source)
                    
                    # Keep the more complete record (prefer non-"Not Available" values)
                    if existing.price == "Not Available" and product.price != "Not Available":
                        existing.price = product.price
                    if existing.image_url == "Not Available" and product.image_url != "Not Available":
                        existing.image_url = product.image_url
                    
                    matched = True
                    break
            
            if not matched:
                # This is a new unique product
                # Initialize sources_list with the current source
                if not product.sources_list:
                    product.sources_list = [product.source]
                deduplicated.append(product)
        
        self.logger.info(f"Deduplication complete: {len(products)} -> {len(deduplicated)} products")
        
        return deduplicated
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity ratio between 0.0 and 1.0
        """
        return SequenceMatcher(None, str1, str2).ratio()

    def _normalize_product(self, product: ProductRecord) -> ProductRecord:
        """
        Normalize product data (trim whitespace, standardize format).
        
        Normalization includes:
        - Trimming leading/trailing whitespace from all string fields
        - Standardizing "Not Available" values
        - Ensuring consistent URL formats
        
        Args:
            product: ProductRecord to normalize
            
        Returns:
            Normalized ProductRecord
        """
        # Trim whitespace from all string fields
        product.name = product.name.strip()
        product.price = product.price.strip()
        product.source = product.source.strip()
        product.link = product.link.strip()
        product.image_url = product.image_url.strip()
        
        # Standardize "Not Available" values (handle variations)
        not_available_variations = ["n/a", "na", "not available", "unavailable", ""]
        
        if product.price.lower() in not_available_variations:
            product.price = "Not Available"
        
        if product.image_url.lower() in not_available_variations:
            product.image_url = "Not Available"
        
        if product.link.lower() in not_available_variations:
            product.link = "Not Available"
        
        self.logger.debug(f"Normalized product: {product.name}")
        
        return product
