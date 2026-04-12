"""Unit tests for TrendAnalyzer class."""

import pytest
from datetime import datetime, timedelta

from src.trend_analyzer import TrendAnalyzer
from src.models import ProductRecord
from src.logger import setup_logger


@pytest.fixture
def logger():
    """Create a test logger."""
    return setup_logger(name="test_trend_analyzer", log_level="DEBUG")


@pytest.fixture
def analyzer(logger):
    """Create a TrendAnalyzer instance."""
    return TrendAnalyzer(logger=logger)


class TestTrendAnalyzerInit:
    """Tests for TrendAnalyzer initialization."""
    
    def test_init_with_logger(self, logger):
        """Test initialization with logger."""
        analyzer = TrendAnalyzer(logger=logger)
        
        assert analyzer.logger == logger


class TestCalculateTrendingScores:
    """Tests for calculate_trending_scores method."""
    
    def test_calculate_trending_scores_single_product(self, analyzer):
        """Test trending score calculation for a single product."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now(),
                mentions=5,
                sources_list=["Amazon", "Flipkart", "Organic Store"]
            )
        ]
        
        result = analyzer.calculate_trending_scores(products)
        
        assert len(result) == 1
        assert result[0][0] == products[0]
        assert 0.0 <= result[0][1] <= 1.0
    
    def test_calculate_trending_scores_multiple_products(self, analyzer):
        """Test trending score calculation for multiple products."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now(),
                mentions=5,
                sources_list=["Amazon", "Flipkart"]
            ),
            ProductRecord(
                name="Organic Tea",
                price="$12.50",
                source="Flipkart",
                link="https://flipkart.com/tea",
                image_url="https://flipkart.com/tea.jpg",
                timestamp=datetime.now() - timedelta(days=10),
                mentions=2,
                sources_list=["Flipkart"]
            )
        ]
        
        result = analyzer.calculate_trending_scores(products)
        
        assert len(result) == 2
        # Recent product with more mentions should score higher
        assert result[0][1] > result[1][1]
    
    def test_calculate_trending_scores_empty_list(self, analyzer):
        """Test trending score calculation with empty list."""
        products = []
        
        result = analyzer.calculate_trending_scores(products)
        
        assert len(result) == 0
    
    def test_calculate_trending_scores_uses_weighted_formula(self, analyzer):
        """Test that trending scores use correct weighted formula."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now(),
                mentions=10,
                sources_list=["Amazon", "Flipkart", "Organic Store"]
            )
        ]
        
        result = analyzer.calculate_trending_scores(products)
        
        product, total_score = result[0]
        
        # Manually calculate expected score
        frequency_score = analyzer._calculate_frequency_score(product)
        recency_score = analyzer._calculate_recency_score(product)
        diversity_score = analyzer._calculate_diversity_score(product)
        
        expected_score = (
            frequency_score * 0.4 +
            recency_score * 0.4 +
            diversity_score * 0.2
        )
        
        assert abs(total_score - expected_score) < 0.001


class TestRankProducts:
    """Tests for rank_products method."""
    
    def test_rank_products_by_score_descending(self, analyzer):
        """Test that products are ranked by score in descending order."""
        products = [
            ProductRecord(
                name="Product A",
                price="$10",
                source="Amazon",
                link="https://amazon.com/a",
                image_url="https://amazon.com/a.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Product B",
                price="$20",
                source="Amazon",
                link="https://amazon.com/b",
                image_url="https://amazon.com/b.jpg",
                timestamp=datetime.now()
            )
        ]
        
        scored_products = [
            (products[0], 0.5),
            (products[1], 0.8)
        ]
        
        result = analyzer.rank_products(scored_products)
        
        assert len(result) == 2
        assert result[0].name == "Product B"  # Higher score
        assert result[1].name == "Product A"  # Lower score
    
    def test_rank_products_alphabetical_tie_breaking(self, analyzer):
        """Test that products with identical scores are ranked alphabetically."""
        products = [
            ProductRecord(
                name="Zebra Product",
                price="$10",
                source="Amazon",
                link="https://amazon.com/z",
                image_url="https://amazon.com/z.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Apple Product",
                price="$20",
                source="Amazon",
                link="https://amazon.com/a",
                image_url="https://amazon.com/a.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Banana Product",
                price="$15",
                source="Amazon",
                link="https://amazon.com/b",
                image_url="https://amazon.com/b.jpg",
                timestamp=datetime.now()
            )
        ]
        
        # All products have the same score
        scored_products = [
            (products[0], 0.7),
            (products[1], 0.7),
            (products[2], 0.7)
        ]
        
        result = analyzer.rank_products(scored_products)
        
        assert len(result) == 3
        assert result[0].name == "Apple Product"
        assert result[1].name == "Banana Product"
        assert result[2].name == "Zebra Product"
    
    def test_rank_products_case_insensitive_alphabetical(self, analyzer):
        """Test that alphabetical tie-breaking is case-insensitive."""
        products = [
            ProductRecord(
                name="zebra product",
                price="$10",
                source="Amazon",
                link="https://amazon.com/z",
                image_url="https://amazon.com/z.jpg",
                timestamp=datetime.now()
            ),
            ProductRecord(
                name="Apple Product",
                price="$20",
                source="Amazon",
                link="https://amazon.com/a",
                image_url="https://amazon.com/a.jpg",
                timestamp=datetime.now()
            )
        ]
        
        scored_products = [
            (products[0], 0.7),
            (products[1], 0.7)
        ]
        
        result = analyzer.rank_products(scored_products)
        
        assert result[0].name == "Apple Product"
        assert result[1].name == "zebra product"
    
    def test_rank_products_empty_list(self, analyzer):
        """Test ranking with empty list."""
        scored_products = []
        
        result = analyzer.rank_products(scored_products)
        
        assert len(result) == 0
    
    def test_rank_products_mixed_scores_and_ties(self, analyzer):
        """Test ranking with mixed scores and ties."""
        products = [
            ProductRecord(name="Product A", price="$10", source="Amazon",
                         link="https://amazon.com/a", image_url="https://amazon.com/a.jpg",
                         timestamp=datetime.now()),
            ProductRecord(name="Product B", price="$20", source="Amazon",
                         link="https://amazon.com/b", image_url="https://amazon.com/b.jpg",
                         timestamp=datetime.now()),
            ProductRecord(name="Product C", price="$15", source="Amazon",
                         link="https://amazon.com/c", image_url="https://amazon.com/c.jpg",
                         timestamp=datetime.now()),
            ProductRecord(name="Product D", price="$25", source="Amazon",
                         link="https://amazon.com/d", image_url="https://amazon.com/d.jpg",
                         timestamp=datetime.now())
        ]
        
        scored_products = [
            (products[0], 0.5),  # Lowest score
            (products[1], 0.8),  # Tied for highest
            (products[2], 0.8),  # Tied for highest
            (products[3], 0.6)   # Middle score
        ]
        
        result = analyzer.rank_products(scored_products)
        
        # Expected order: B and C (0.8, alphabetical), D (0.6), A (0.5)
        assert result[0].name == "Product B"
        assert result[1].name == "Product C"
        assert result[2].name == "Product D"
        assert result[3].name == "Product A"


class TestGetTopN:
    """Tests for get_top_n method."""
    
    def test_get_top_n_default_five(self, analyzer):
        """Test getting top 5 products by default."""
        products = [
            ProductRecord(name=f"Product {i}", price="$10", source="Amazon",
                         link=f"https://amazon.com/{i}", image_url=f"https://amazon.com/{i}.jpg",
                         timestamp=datetime.now(), mentions=i)
            for i in range(10)
        ]
        
        result = analyzer.get_top_n(products)
        
        assert len(result) == 5
        assert result == products[:5]
    
    def test_get_top_n_custom_count(self, analyzer):
        """Test getting custom number of top products."""
        products = [
            ProductRecord(name=f"Product {i}", price="$10", source="Amazon",
                         link=f"https://amazon.com/{i}", image_url=f"https://amazon.com/{i}.jpg",
                         timestamp=datetime.now(), mentions=i)
            for i in range(10)
        ]
        
        result = analyzer.get_top_n(products, n=3)
        
        assert len(result) == 3
        assert result == products[:3]
    
    def test_get_top_n_fewer_than_n_products(self, analyzer):
        """Test getting top N when fewer than N products exist."""
        products = [
            ProductRecord(name=f"Product {i}", price="$10", source="Amazon",
                         link=f"https://amazon.com/{i}", image_url=f"https://amazon.com/{i}.jpg",
                         timestamp=datetime.now(), mentions=i)
            for i in range(3)
        ]
        
        result = analyzer.get_top_n(products, n=5)
        
        assert len(result) == 3
        assert result == products
    
    def test_get_top_n_empty_list(self, analyzer):
        """Test getting top N from empty list."""
        products = []
        
        result = analyzer.get_top_n(products)
        
        assert len(result) == 0


class TestCalculateFrequencyScore:
    """Tests for _calculate_frequency_score method."""
    
    def test_calculate_frequency_score_single_mention(self, analyzer):
        """Test frequency score for product with single mention."""
        product = ProductRecord(
            name="Organic Honey",
            price="$15.99",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="https://amazon.com/honey.jpg",
            timestamp=datetime.now(),
            mentions=1
        )
        
        score = analyzer._calculate_frequency_score(product)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.0  # Should have some score even with 1 mention
    
    def test_calculate_frequency_score_multiple_mentions(self, analyzer):
        """Test frequency score increases with more mentions."""
        product_low = ProductRecord(
            name="Product A",
            price="$10",
            source="Amazon",
            link="https://amazon.com/a",
            image_url="https://amazon.com/a.jpg",
            timestamp=datetime.now(),
            mentions=2
        )
        
        product_high = ProductRecord(
            name="Product B",
            price="$20",
            source="Amazon",
            link="https://amazon.com/b",
            image_url="https://amazon.com/b.jpg",
            timestamp=datetime.now(),
            mentions=10
        )
        
        score_low = analyzer._calculate_frequency_score(product_low)
        score_high = analyzer._calculate_frequency_score(product_high)
        
        assert score_high > score_low
    
    def test_calculate_frequency_score_range(self, analyzer):
        """Test that frequency score is always in [0.0, 1.0] range."""
        test_mentions = [1, 5, 10, 50, 100, 200]
        
        for mentions in test_mentions:
            product = ProductRecord(
                name="Product",
                price="$10",
                source="Amazon",
                link="https://amazon.com/p",
                image_url="https://amazon.com/p.jpg",
                timestamp=datetime.now(),
                mentions=mentions
            )
            
            score = analyzer._calculate_frequency_score(product)
            
            assert 0.0 <= score <= 1.0


class TestCalculateRecencyScore:
    """Tests for _calculate_recency_score method."""
    
    def test_calculate_recency_score_past_24_hours(self, analyzer):
        """Test recency score for product within past 24 hours."""
        product = ProductRecord(
            name="Organic Honey",
            price="$15.99",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="https://amazon.com/honey.jpg",
            timestamp=datetime.now() - timedelta(hours=12)
        )
        
        score = analyzer._calculate_recency_score(product)
        
        assert score == 1.0
    
    def test_calculate_recency_score_past_7_days(self, analyzer):
        """Test recency score for product within past 7 days."""
        product = ProductRecord(
            name="Organic Honey",
            price="$15.99",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="https://amazon.com/honey.jpg",
            timestamp=datetime.now() - timedelta(days=5)
        )
        
        score = analyzer._calculate_recency_score(product)
        
        assert score == 0.7
    
    def test_calculate_recency_score_past_30_days(self, analyzer):
        """Test recency score for product within past 30 days."""
        product = ProductRecord(
            name="Organic Honey",
            price="$15.99",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="https://amazon.com/honey.jpg",
            timestamp=datetime.now() - timedelta(days=20)
        )
        
        score = analyzer._calculate_recency_score(product)
        
        assert score == 0.4
    
    def test_calculate_recency_score_older_than_30_days(self, analyzer):
        """Test recency score for product older than 30 days."""
        product = ProductRecord(
            name="Organic Honey",
            price="$15.99",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="https://amazon.com/honey.jpg",
            timestamp=datetime.now() - timedelta(days=60)
        )
        
        score = analyzer._calculate_recency_score(product)
        
        assert score == 0.1
    
    def test_calculate_recency_score_boundary_24_hours(self, analyzer):
        """Test recency score at 24-hour boundary."""
        product = ProductRecord(
            name="Organic Honey",
            price="$15.99",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="https://amazon.com/honey.jpg",
            timestamp=datetime.now() - timedelta(hours=24)
        )
        
        score = analyzer._calculate_recency_score(product)
        
        assert score == 1.0
    
    def test_calculate_recency_score_boundary_7_days(self, analyzer):
        """Test recency score at 7-day boundary."""
        product = ProductRecord(
            name="Organic Honey",
            price="$15.99",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="https://amazon.com/honey.jpg",
            timestamp=datetime.now() - timedelta(days=7)
        )
        
        score = analyzer._calculate_recency_score(product)
        
        assert score == 0.7
    
    def test_calculate_recency_score_recent_higher_than_old(self, analyzer):
        """Test that recent products score higher than old products."""
        product_recent = ProductRecord(
            name="Product A",
            price="$10",
            source="Amazon",
            link="https://amazon.com/a",
            image_url="https://amazon.com/a.jpg",
            timestamp=datetime.now() - timedelta(hours=1)
        )
        
        product_old = ProductRecord(
            name="Product B",
            price="$20",
            source="Amazon",
            link="https://amazon.com/b",
            image_url="https://amazon.com/b.jpg",
            timestamp=datetime.now() - timedelta(days=100)
        )
        
        score_recent = analyzer._calculate_recency_score(product_recent)
        score_old = analyzer._calculate_recency_score(product_old)
        
        assert score_recent > score_old


class TestCalculateDiversityScore:
    """Tests for _calculate_diversity_score method."""
    
    def test_calculate_diversity_score_single_source(self, analyzer):
        """Test diversity score for product from single source."""
        product = ProductRecord(
            name="Organic Honey",
            price="$15.99",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="https://amazon.com/honey.jpg",
            timestamp=datetime.now(),
            sources_list=["Amazon"]
        )
        
        score = analyzer._calculate_diversity_score(product)
        
        assert score == 0.1  # 1/10
    
    def test_calculate_diversity_score_multiple_sources(self, analyzer):
        """Test diversity score increases with more sources."""
        product_low = ProductRecord(
            name="Product A",
            price="$10",
            source="Amazon",
            link="https://amazon.com/a",
            image_url="https://amazon.com/a.jpg",
            timestamp=datetime.now(),
            sources_list=["Amazon"]
        )
        
        product_high = ProductRecord(
            name="Product B",
            price="$20",
            source="Amazon",
            link="https://amazon.com/b",
            image_url="https://amazon.com/b.jpg",
            timestamp=datetime.now(),
            sources_list=["Amazon", "Flipkart", "Organic Store", "Social Media"]
        )
        
        score_low = analyzer._calculate_diversity_score(product_low)
        score_high = analyzer._calculate_diversity_score(product_high)
        
        assert score_high > score_low
    
    def test_calculate_diversity_score_empty_sources_list(self, analyzer):
        """Test diversity score when sources_list is empty."""
        product = ProductRecord(
            name="Organic Honey",
            price="$15.99",
            source="Amazon",
            link="https://amazon.com/honey",
            image_url="https://amazon.com/honey.jpg",
            timestamp=datetime.now(),
            sources_list=[]
        )
        
        score = analyzer._calculate_diversity_score(product)
        
        assert score == 0.1  # Defaults to 1 source
    
    def test_calculate_diversity_score_range(self, analyzer):
        """Test that diversity score is always in [0.0, 1.0] range."""
        test_source_counts = [1, 3, 5, 10, 15]
        
        for count in test_source_counts:
            product = ProductRecord(
                name="Product",
                price="$10",
                source="Amazon",
                link="https://amazon.com/p",
                image_url="https://amazon.com/p.jpg",
                timestamp=datetime.now(),
                sources_list=[f"Source{i}" for i in range(count)]
            )
            
            score = analyzer._calculate_diversity_score(product)
            
            assert 0.0 <= score <= 1.0
    
    def test_calculate_diversity_score_max_sources(self, analyzer):
        """Test diversity score with maximum sources."""
        product = ProductRecord(
            name="Product",
            price="$10",
            source="Amazon",
            link="https://amazon.com/p",
            image_url="https://amazon.com/p.jpg",
            timestamp=datetime.now(),
            sources_list=[f"Source{i}" for i in range(10)]
        )
        
        score = analyzer._calculate_diversity_score(product)
        
        assert score == 1.0


class TestIntegration:
    """Integration tests for TrendAnalyzer."""
    
    def test_full_trend_analysis_workflow(self, analyzer):
        """Test complete trend analysis workflow."""
        products = [
            ProductRecord(
                name="Organic Honey",
                price="$15.99",
                source="Amazon",
                link="https://amazon.com/honey",
                image_url="https://amazon.com/honey.jpg",
                timestamp=datetime.now() - timedelta(hours=2),
                mentions=10,
                sources_list=["Amazon", "Flipkart", "Organic Store"]
            ),
            ProductRecord(
                name="Organic Tea",
                price="$12.50",
                source="Flipkart",
                link="https://flipkart.com/tea",
                image_url="https://flipkart.com/tea.jpg",
                timestamp=datetime.now() - timedelta(days=10),
                mentions=5,
                sources_list=["Flipkart", "Organic Store"]
            ),
            ProductRecord(
                name="Organic Coffee",
                price="$18.00",
                source="Amazon",
                link="https://amazon.com/coffee",
                image_url="https://amazon.com/coffee.jpg",
                timestamp=datetime.now() - timedelta(hours=1),
                mentions=8,
                sources_list=["Amazon", "Flipkart"]
            )
        ]
        
        # Calculate scores
        scored_products = analyzer.calculate_trending_scores(products)
        
        # Rank products
        ranked_products = analyzer.rank_products(scored_products)
        
        # Get top 2
        top_products = analyzer.get_top_n(ranked_products, n=2)
        
        assert len(top_products) == 2
        # Coffee and Honey should be top (recent, high mentions)
        # Tea should be lower (older timestamp)
        assert top_products[0].name in ["Organic Coffee", "Organic Honey"]
        assert top_products[1].name in ["Organic Coffee", "Organic Honey"]
    
    def test_trend_analysis_with_ties(self, analyzer):
        """Test trend analysis with products having identical scores."""
        products = [
            ProductRecord(
                name="Zebra Product",
                price="$10",
                source="Amazon",
                link="https://amazon.com/z",
                image_url="https://amazon.com/z.jpg",
                timestamp=datetime.now(),
                mentions=5,
                sources_list=["Amazon", "Flipkart"]
            ),
            ProductRecord(
                name="Apple Product",
                price="$20",
                source="Amazon",
                link="https://amazon.com/a",
                image_url="https://amazon.com/a.jpg",
                timestamp=datetime.now(),
                mentions=5,
                sources_list=["Amazon", "Flipkart"]
            )
        ]
        
        scored_products = analyzer.calculate_trending_scores(products)
        ranked_products = analyzer.rank_products(scored_products)
        
        # Should be alphabetically ordered
        assert ranked_products[0].name == "Apple Product"
        assert ranked_products[1].name == "Zebra Product"
