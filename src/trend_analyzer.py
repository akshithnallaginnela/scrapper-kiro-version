"""Trend analysis and product ranking for the Organic Products Web Scraper."""

import logging
from typing import List, Tuple
from datetime import datetime, timedelta
from src.models import ProductRecord, TrendingScore


class TrendAnalyzer:
    """Analyzes product trends and calculates ranking scores."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize with logger.
        
        Args:
            logger: Logger instance for recording trend analysis activities
        """
        self.logger = logger
        self.logger.info("TrendAnalyzer initialized")
    
    def calculate_trending_scores(
        self, 
        products: List[ProductRecord]
    ) -> List[Tuple[ProductRecord, float]]:
        """
        Calculate trending score for each product.
        
        Uses weighted scoring based on:
        - Frequency score (40%): Based on mention count across sources
        - Recency score (40%): Based on timestamp recency
        - Diversity score (20%): Based on source diversity
        
        Args:
            products: List of ProductRecords to score
            
        Returns:
            List of (product, score) tuples
        """
        self.logger.info(f"Calculating trending scores for {len(products)} products")
        
        scored_products = []
        
        for product in products:
            # Calculate individual score components
            frequency_score = self._calculate_frequency_score(product)
            recency_score = self._calculate_recency_score(product)
            diversity_score = self._calculate_diversity_score(product)
            
            # Create TrendingScore object
            trending_score = TrendingScore(
                product=product,
                frequency_score=frequency_score,
                recency_score=recency_score,
                diversity_score=diversity_score
            )
            
            # Calculate weighted total score
            total_score = trending_score.calculate_total(
                frequency_weight=0.4,
                recency_weight=0.4,
                diversity_weight=0.2
            )
            
            self.logger.debug(
                f"Product '{product.name}': "
                f"frequency={frequency_score:.3f}, "
                f"recency={recency_score:.3f}, "
                f"diversity={diversity_score:.3f}, "
                f"total={total_score:.3f}"
            )
            
            scored_products.append((product, total_score))
        
        self.logger.info("Trending score calculation complete")
        
        return scored_products
    
    def rank_products(
        self, 
        scored_products: List[Tuple[ProductRecord, float]]
    ) -> List[ProductRecord]:
        """
        Rank products by score (descending).
        Tie-breaking by alphabetical order.
        
        Args:
            scored_products: List of (product, score) tuples
            
        Returns:
            List of ProductRecords sorted by score (descending), then alphabetically
        """
        self.logger.info(f"Ranking {len(scored_products)} products")
        
        # Sort by score (descending), then by name (ascending) for tie-breaking
        sorted_products = sorted(
            scored_products,
            key=lambda x: (-x[1], x[0].name.lower())
        )
        
        # Extract just the products (without scores)
        ranked_products = [product for product, score in sorted_products]
        
        # Log top products
        if ranked_products:
            self.logger.info(f"Top ranked product: '{ranked_products[0].name}'")
        
        return ranked_products
    
    def get_top_n(
        self, 
        ranked_products: List[ProductRecord], 
        n: int = 5
    ) -> List[ProductRecord]:
        """
        Return top N products.
        
        Args:
            ranked_products: List of ranked ProductRecords
            n: Number of top products to return (default: 5)
            
        Returns:
            List of top N ProductRecords
        """
        top_products = ranked_products[:n]
        
        self.logger.info(f"Selected top {len(top_products)} products")
        
        for i, product in enumerate(top_products, 1):
            self.logger.info(f"  {i}. {product.name} (mentions: {product.mentions})")
        
        return top_products
    
    def _calculate_frequency_score(self, product: ProductRecord) -> float:
        """
        Calculate score based on mention frequency.
        
        Normalizes mention count to a 0.0-1.0 scale using logarithmic scaling
        to prevent products with extremely high mention counts from dominating.
        
        Args:
            product: ProductRecord to score
            
        Returns:
            Frequency score between 0.0 and 1.0
        """
        # Use logarithmic scaling to normalize mention counts
        # log(mentions + 1) to handle mentions=1 case
        import math
        
        # Assume max mentions of 100 for normalization (can be adjusted)
        max_mentions = 100
        normalized_score = math.log(product.mentions + 1) / math.log(max_mentions + 1)
        
        # Clamp to [0.0, 1.0] range
        return min(1.0, max(0.0, normalized_score))
    
    def _calculate_recency_score(self, product: ProductRecord) -> float:
        """
        Calculate score based on mention recency.
        
        Implements tiered scoring:
        - Within past 24 hours: 1.0 (highest priority for social media)
        - Within past 7 days: 0.7 (high priority for search results)
        - Within past 30 days: 0.4 (moderate priority)
        - Older than 30 days: 0.1 (low priority)
        
        Args:
            product: ProductRecord to score
            
        Returns:
            Recency score between 0.0 and 1.0
        """
        now = datetime.now()
        age = now - product.timestamp
        
        if age <= timedelta(hours=24):
            # Very recent (past 24 hours) - highest score
            return 1.0
        elif age <= timedelta(days=7):
            # Recent (past 7 days) - high score
            return 0.7
        elif age <= timedelta(days=30):
            # Moderate age (past 30 days) - moderate score
            return 0.4
        else:
            # Old (older than 30 days) - low score
            return 0.1
    
    def _calculate_diversity_score(self, product: ProductRecord) -> float:
        """
        Calculate score based on source diversity.
        
        Products mentioned across multiple sources are considered more
        significant than products from a single source.
        
        Args:
            product: ProductRecord to score
            
        Returns:
            Diversity score between 0.0 and 1.0
        """
        # Number of unique sources mentioning this product
        source_count = len(product.sources_list) if product.sources_list else 1
        
        # Assume max of 10 sources for normalization
        max_sources = 10
        normalized_score = source_count / max_sources
        
        # Clamp to [0.0, 1.0] range
        return min(1.0, max(0.0, normalized_score))
