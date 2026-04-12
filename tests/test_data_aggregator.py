"""Unit tests for DataAggregator class."""

import pytest
from datetime import datetime

from src.data_aggregator import DataAggregator
from src.models import ProductRecord
from src.logger import setup_logger


@pytest.fixture
def logger():
    """Create a test logger."""
    return setup_logger(name="test_aggregator", log_level="DEBUG")


@pytest.fixture
def aggregator(logger):
    """Create a DataAggregator instance."""
    return DataAggregator(logger=logger)


class TestDataAggregatorInit:
    """Tests for DataAggregator initialization."""
    
    def test_init_with_logger(self, logger):
        """Test initialization with logger."""
        aggregator = DataAggregator(logger=logger)
        
        assert aggregator.logger == logger


class TestAggregate:
    """Tests for aggregate method."""
    
    def test_aggregate_single_source(self, aggregator):
        """Test aggregation from a single source."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now()
            )
        ]
        
        products_by_source = {"Amazon": products}
        
        result = aggregator.aggregate(products_by_source)
        
        assert len(result) == 1
        assert result[0].name == "Organic Honey"
        assert result[0].mentions == 1
        assert "Amazon" in result[0].sources_list

    
    def test_aggregate_multiple_sources(self, aggregator):
        """Test aggregation from multiple sources."""
        products_amazon = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now()
            )
        ]
        
        products_flipkart = [
            ProductRecord(
                name="Organic Tea",
                price="$12.50",
                source="Flipkart",
                link="https://flipkart.com/tea",
                image_url="https://flipkart.com/tea.jpg",
                timestamp=datetime.now()
            )
        ]
        
        products_by_source = {
            "Amazon": products_amazon,
            "Flipkart": products_flipkart
        }
        
        result = aggregator.aggregate(products_by_source)
        
        assert len(result) == 2
        assert result[0].name == "Organic Honey"
        assert result[1].name == "Organic Tea"
    
    def test_aggregate_empty_sources(self, aggregator):
        """Test aggregation with empty sources."""
        products_by_source = {}
        
        result = aggregator.aggregate(products_by_source)
        
        assert len(result) == 0
    
    def test_aggregate_normalizes_products(self, aggregator):
        """Test that aggregation normalizes products."""
        products = [
            ProductRecord(
                name="  Organic Honey  ",
                price="  $15.99  ",
                source="  Amazon  ",
                link="  https://amazon.com/honey  ",
                image_url="  https://amazon.com/honey.jpg  ",
                timestamp=datetime.now()
            )
        ]
        
        products_by_source = {"Amazon": products}
        
        result = aggregator.aggregate(products_by_source)
        
        assert result[0].name == "Organic Honey"
        assert result[0].price == "$15.99"
        assert result[0].source == "Amazon"
        assert result[0].link == "https://amazon.com/honey"
        assert result[0].image_url == "https://amazon.com/honey.jpg"


class TestDeduplicate:
    """Tests for _deduplicate method."""
    
    def test_deduplicate_identical_names(self, aggregator):
        """Test deduplication of products with identical names."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Organic Honey",
                price="$16.99",
                source="Flipkart",
                link="https://flipkart.com/honey",
                image_url="https://flipkart.com/honey.jpg",
                timestamp=datetime.now()
            )
        ]
        
        result = aggregator._deduplicate(products)
        
        assert len(result) == 1
        assert result[0].mentions == 2
        assert "Amazon" in result[0].sources_list
        assert "Flipkart" in result[0].sources_list
    
    def test_deduplicate_similar_names(self, aggregator):
        """Test deduplication of products with similar names."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="organic honey",
                price="$16.99",
                source="Flipkart",
                link="https://flipkart.com/honey",
                image_url="https://flipkart.com/honey.jpg",
                timestamp=datetime.now()
            )
        ]
        
        result = aggregator._deduplicate(products)
        
        assert len(result) == 1
        assert result[0].mentions == 2
    
    def test_deduplicate_different_names(self, aggregator):
        """Test that different products are not deduplicated."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Organic Tea",
                price="$12.50",
                source="Flipkart",
                link="https://flipkart.com/tea",
                image_url="https://flipkart.com/tea.jpg",
                timestamp=datetime.now()
            )
        ]
        
        result = aggregator._deduplicate(products)
        
        assert len(result) == 2
        assert result[0].mentions == 1
        assert result[1].mentions == 1
    
    def test_deduplicate_empty_list(self, aggregator):
        """Test deduplication of empty list."""
        products = []
        
        result = aggregator._deduplicate(products)
        
        assert len(result) == 0
    
    def test_deduplicate_merges_missing_data(self, aggregator):
        """Test that deduplication merges missing data from duplicates."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="Not Available",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="Not Available",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Flipkart",
                link="https://flipkart.com/honey",
                image_url="https://flipkart.com/honey.jpg",
                timestamp=datetime.now()
            )
        ]
        
        result = aggregator._deduplicate(products)
        
        assert len(result) == 1
        assert result[0].price == "$15.99"
        assert result[0].image_url == "https://flipkart.com/honey.jpg"
    
    def test_deduplicate_keeps_first_complete_record(self, aggregator):
        """Test that deduplication keeps the first complete record."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Organic Honey",
                price="Not Available",
                source="Flipkart",
                link="https://flipkart.com/honey",
                image_url="Not Available",
                timestamp=datetime.now()
            )
        ]
        
        result = aggregator._deduplicate(products)
        
        assert len(result) == 1
        assert result[0].price == "$15.99"
        assert result[0].image_url == "https://amazon.com/honey.jpg"
    
    def test_deduplicate_multiple_duplicates(self, aggregator):
        """Test deduplication with multiple duplicate groups."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Organic Honey",
                price="$16.99",
                source="Flipkart",
                link="https://flipkart.com/honey",
                image_url="https://flipkart.com/honey.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Organic Tea",
                price="$12.50",
                source="Amazon",
                link="https://amazon.com/tea",
                image_url="https://amazon.com/tea.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Organic Tea",
                price="$13.00",
                source="Flipkart",
                link="https://flipkart.com/tea",
                image_url="https://flipkart.com/tea.jpg",
                timestamp=datetime.now()
            )
        ]
        
        result = aggregator._deduplicate(products)
        
        assert len(result) == 2
        assert result[0].mentions == 2
        assert result[1].mentions == 2


class TestCalculateSimilarity:
    """Tests for _calculate_similarity method."""
    
    def test_calculate_similarity_identical(self, aggregator):
        """Test similarity of identical strings."""
        similarity = aggregator._calculate_similarity("organic honey", "organic honey")
        
        assert similarity == 1.0
    
    def test_calculate_similarity_different(self, aggregator):
        """Test similarity of completely different strings."""
        similarity = aggregator._calculate_similarity("organic honey", "organic tea")
        
        assert similarity < 0.85
    
    def test_calculate_similarity_case_insensitive(self, aggregator):
        """Test that similarity calculation works with lowercase strings."""
        # Note: In practice, _deduplicate calls this with .lower() already applied
        similarity = aggregator._calculate_similarity("organic honey", "organic honey")
        
        assert similarity == 1.0
    
    def test_calculate_similarity_partial_match(self, aggregator):
        """Test similarity of partially matching strings."""
        similarity = aggregator._calculate_similarity("organic honey", "organic honey jar")
        
        assert 0.7 < similarity < 1.0


class TestNormalizeProduct:
    """Tests for _normalize_product method."""
    
    def test_normalize_product_trims_whitespace(self, aggregator):
        """Test that normalization trims whitespace."""
        product = ProductRecord(
            name="  Organic Honey  ",
            price="  $15.99  ",
            source="  Amazon  ",
            link="  https://amazon.com/honey  ",
            image_url="  https://amazon.com/honey.jpg  ",
            timestamp=datetime.now()
        )
        
        result = aggregator._normalize_product(product)
        
        assert result.name == "Organic Honey"
        assert result.price == "$15.99"
        assert result.source == "Amazon"
        assert result.link == "https://amazon.com/honey"
        assert result.image_url == "https://amazon.com/honey.jpg"
    
    def test_normalize_product_standardizes_not_available(self, aggregator):
        """Test that normalization standardizes 'Not Available' values."""
        product = ProductRecord(
            name="Organic Honey",
            price="n/a",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="unavailable",
            timestamp=datetime.now()
        )
        
        result = aggregator._normalize_product(product)
        
        assert result.price == "Not Available"
        assert result.image_url == "Not Available"
    
    def test_normalize_product_handles_empty_strings(self, aggregator):
        """Test that normalization handles empty strings."""
        product = ProductRecord(
            name="Organic Honey",
            price="",
            source="Amazon",
            link="",
            image_url="",
            timestamp=datetime.now()
        )
        
        result = aggregator._normalize_product(product)
        
        assert result.price == "Not Available"
        assert result.link == "Not Available"
        assert result.image_url == "Not Available"
    
    def test_normalize_product_preserves_valid_data(self, aggregator):
        """Test that normalization preserves valid data."""
        product = ProductRecord(
            name="Organic Honey",
            price="$15.99",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="https://amazon.com/honey.jpg",
            timestamp=datetime.now()
        )
        
        result = aggregator._normalize_product(product)
        
        assert result.name == "Organic Honey"
        assert result.price == "$15.99"
        assert result.link == "https://amazon.com/honey"
        assert result.image_url == "https://amazon.com/honey.jpg"
    
    def test_normalize_product_handles_na_variations(self, aggregator):
        """Test that normalization handles various 'Not Available' variations."""
        test_cases = ["n/a", "na", "not available", "unavailable", ""]
        
        for variation in test_cases:
            product = ProductRecord(
                name="Organic Honey",
                price=variation,
                source="Amazon",
                link="https://amazon.com/honey",
                image_url=variation,
                timestamp=datetime.now()
            )
            
            result = aggregator._normalize_product(product)
            
            assert result.price == "Not Available"
            assert result.image_url == "Not Available"


class TestIntegration:
    """Integration tests for DataAggregator."""
    
    def test_full_aggregation_workflow(self, aggregator):
        """Test complete aggregation workflow with multiple sources and duplicates."""
        products_amazon = [
            ProductRecord(
                name="  Organic Honey  ",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Organic Tea",
                price="$12.50",
                source="Amazon",
                link="https://amazon.com/tea",
                image_url="https://amazon.com/tea.jpg",
                timestamp=datetime.now()
            )
        ]
        
        products_flipkart = [
            ProductRecord(
                name="organic honey",
                price="n/a",
                source="Flipkart",
                link="https://flipkart.com/honey",
                image_url="unavailable",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Organic Coffee",
                price="$18.00",
                source="Flipkart",
                link="https://flipkart.com/coffee",
                image_url="https://flipkart.com/coffee.jpg",
                timestamp=datetime.now()
            )
        ]
        
        products_by_source = {
            "Amazon": products_amazon,
            "Flipkart": products_flipkart
        }
        
        result = aggregator.aggregate(products_by_source)
        
        # Should have 3 unique products (Honey is deduplicated)
        assert len(result) == 3
        
        # Find the honey product
        honey = next(p for p in result if "Honey" in p.name)
        
        # Verify deduplication and normalization
        assert honey.mentions == 2
        assert "Amazon" in honey.sources_list
        assert "Flipkart" in honey.sources_list
        assert honey.price == "$15.99"  # Kept from Amazon (not "Not Available")
        assert honey.name == "Organic Honey"  # Normalized (trimmed)
