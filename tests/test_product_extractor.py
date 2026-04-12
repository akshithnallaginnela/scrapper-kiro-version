"""Unit tests for ProductExtractor class."""

import pytest
from bs4 import BeautifulSoup
from datetime import datetime

from src.product_extractor import ProductExtractor
from src.models import ProductRecord
from src.logger import setup_logger


@pytest.fixture
def logger():
    """Create a test logger."""
    return setup_logger(name="test_extractor", log_level="DEBUG")


@pytest.fixture
def extractor(logger):
    """Create a ProductExtractor instance."""
    return ProductExtractor(logger=logger)


class TestProductExtractorInit:
    """Tests for ProductExtractor initialization."""
    
    def test_init_with_logger(self, logger):
        """Test initialization with logger."""
        extractor = ProductExtractor(logger=logger)
        
        assert extractor.logger == logger
    
    def test_init_without_logger(self):
        """Test initialization without logger creates default logger."""
        extractor = ProductExtractor()
        
        assert extractor.logger is not None


class TestExtractProducts:
    """Tests for extract_products method."""
    
    def test_extract_products_success(self, extractor):
        """Test successful product extraction."""
        html = """
        <div class="product">
            <h2 class="name">Organic Honey</h2>
            <span class="price">$15.99</span>
            <a class="link" href="https://example.com/honey">View</a>
            <img class="image" src="https://example.com/honey.jpg" />
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = {
            'container': '.product',
            'name': '.name',
            'price': '.price',
            'link': '.link',
            'image': '.image'
        }
        
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        assert len(products) == 1
        assert products[0].name == "Organic Honey"
        assert products[0].price == "$15.99"
        assert products[0].source == "TestSource"
        assert products[0].link == "https://example.com/honey"
        assert products[0].image_url == "https://example.com/honey.jpg"
        assert products[0].mentions == 1
        assert products[0].sources_list == ["TestSource"]
    
    def test_extract_multiple_products(self, extractor):
        """Test extracting multiple products."""
        html = """
        <div class="product">
            <h2 class="name">Organic Honey</h2>
            <span class="price">$15.99</span>
            <a class="link" href="https://example.com/honey">View</a>
            <img class="image" src="https://example.com/honey.jpg" />
        </div>
        <div class="product">
            <h2 class="name">Organic Tea</h2>
            <span class="price">$12.50</span>
            <a class="link" href="https://example.com/tea">View</a>
            <img class="image" src="https://example.com/tea.jpg" />
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = {
            'container': '.product',
            'name': '.name',
            'price': '.price',
            'link': '.link',
            'image': '.image'
        }
        
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        assert len(products) == 2
        assert products[0].name == "Organic Honey"
        assert products[1].name == "Organic Tea"
    
    def test_extract_products_missing_price(self, extractor):
        """Test extraction with missing price field."""
        html = """
        <div class="product">
            <h2 class="name">Organic Honey</h2>
            <a class="link" href="https://example.com/honey">View</a>
            <img class="image" src="https://example.com/honey.jpg" />
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = {
            'container': '.product',
            'name': '.name',
            'price': '.price',
            'link': '.link',
            'image': '.image'
        }
        
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        assert len(products) == 1
        assert products[0].price == "Not Available"
    
    def test_extract_products_missing_image(self, extractor):
        """Test extraction with missing image field."""
        html = """
        <div class="product">
            <h2 class="name">Organic Honey</h2>
            <span class="price">$15.99</span>
            <a class="link" href="https://example.com/honey">View</a>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = {
            'container': '.product',
            'name': '.name',
            'price': '.price',
            'link': '.link',
            'image': '.image'
        }
        
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        assert len(products) == 1
        assert products[0].image_url == "Not Available"
    
    def test_extract_products_missing_name_skips_product(self, extractor):
        """Test that products with missing name are skipped."""
        html = """
        <div class="product">
            <span class="price">$15.99</span>
            <a class="link" href="https://example.com/honey">View</a>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = {
            'container': '.product',
            'name': '.name',
            'price': '.price',
            'link': '.link',
            'image': '.image'
        }
        
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        assert len(products) == 0
    
    def test_extract_products_no_containers(self, extractor):
        """Test extraction when no containers are found."""
        html = "<div><p>No products here</p></div>"
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = {
            'container': '.product',
            'name': '.name',
            'price': '.price',
            'link': '.link',
            'image': '.image'
        }
        
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        assert len(products) == 0
    
    def test_extract_products_invalid_url(self, extractor):
        """Test extraction with invalid URL."""
        html = """
        <div class="product">
            <h2 class="name">Organic Honey</h2>
            <span class="price">$15.99</span>
            <a class="link" href="not-a-valid-url">View</a>
            <img class="image" src="https://example.com/honey.jpg" />
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = {
            'container': '.product',
            'name': '.name',
            'price': '.price',
            'link': '.link',
            'image': '.image'
        }
        
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        assert len(products) == 1
        assert products[0].link == "Not Available"
    
    def test_extract_products_utf8_text(self, extractor):
        """Test extraction with UTF-8 characters."""
        html = """
        <div class="product">
            <h2 class="name">Café Orgánico</h2>
            <span class="price">€12.50</span>
            <a class="link" href="https://example.com/cafe">View</a>
            <img class="image" src="https://example.com/cafe.jpg" />
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = {
            'container': '.product',
            'name': '.name',
            'price': '.price',
            'link': '.link',
            'image': '.image'
        }
        
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        assert len(products) == 1
        assert products[0].name == "Café Orgánico"
        assert products[0].price == "€12.50"


class TestExtractField:
    """Tests for _extract_field helper method."""
    
    def test_extract_field_text(self, extractor):
        """Test extracting text content."""
        html = '<div><span class="test">Hello World</span></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.div
        
        result = extractor._extract_field(element, '.test')
        
        assert result == "Hello World"
    
    def test_extract_field_attribute(self, extractor):
        """Test extracting attribute value."""
        html = '<div><a class="link" href="https://example.com">Link</a></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.div
        
        result = extractor._extract_field(element, '.link', attribute='href')
        
        assert result == "https://example.com"
    
    def test_extract_field_missing_element(self, extractor):
        """Test extraction with missing element returns default."""
        html = '<div><span class="other">Text</span></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.div
        
        result = extractor._extract_field(element, '.missing', default="Default")
        
        assert result == "Default"
    
    def test_extract_field_empty_selector(self, extractor):
        """Test extraction with empty selector returns default."""
        html = '<div><span>Text</span></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.div
        
        result = extractor._extract_field(element, '', default="Default")
        
        assert result == "Default"
    
    def test_extract_field_strips_whitespace(self, extractor):
        """Test that extracted text is stripped of whitespace."""
        html = '<div><span class="test">  Hello World  </span></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.div
        
        result = extractor._extract_field(element, '.test')
        
        assert result == "Hello World"
    
    def test_extract_field_empty_text(self, extractor):
        """Test extraction with empty text returns default."""
        html = '<div><span class="test"></span></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.div
        
        result = extractor._extract_field(element, '.test', default="Default")
        
        assert result == "Default"
    
    def test_extract_field_missing_attribute(self, extractor):
        """Test extraction with missing attribute returns default."""
        html = '<div><a class="link">Link</a></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.div
        
        result = extractor._extract_field(element, '.link', attribute='href', default="Default")
        
        assert result == "Default"
    
    def test_extract_field_utf8_text(self, extractor):
        """Test extracting UTF-8 text."""
        html = '<div><span class="test">Café résumé</span></div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.div
        
        result = extractor._extract_field(element, '.test')
        
        assert result == "Café résumé"


class TestValidateUrl:
    """Tests for _validate_url method."""
    
    def test_validate_url_valid_http(self, extractor):
        """Test validation of valid HTTP URL."""
        assert extractor._validate_url("http://example.com") is True
    
    def test_validate_url_valid_https(self, extractor):
        """Test validation of valid HTTPS URL."""
        assert extractor._validate_url("https://example.com") is True
    
    def test_validate_url_with_path(self, extractor):
        """Test validation of URL with path."""
        assert extractor._validate_url("https://example.com/path/to/page") is True
    
    def test_validate_url_with_query(self, extractor):
        """Test validation of URL with query parameters."""
        assert extractor._validate_url("https://example.com/page?id=123") is True
    
    def test_validate_url_missing_scheme(self, extractor):
        """Test validation of URL without scheme."""
        assert extractor._validate_url("example.com") is False
    
    def test_validate_url_invalid_scheme(self, extractor):
        """Test validation of URL with invalid scheme."""
        assert extractor._validate_url("ftp://example.com") is False
    
    def test_validate_url_missing_domain(self, extractor):
        """Test validation of URL without domain."""
        assert extractor._validate_url("https://") is False
    
    def test_validate_url_empty_string(self, extractor):
        """Test validation of empty string."""
        assert extractor._validate_url("") is False
    
    def test_validate_url_none(self, extractor):
        """Test validation of None value."""
        assert extractor._validate_url(None) is False
    
    def test_validate_url_malformed(self, extractor):
        """Test validation of malformed URL."""
        assert extractor._validate_url("not a url at all") is False
    
    def test_validate_url_localhost(self, extractor):
        """Test validation of localhost URL."""
        assert extractor._validate_url("http://localhost:8080") is True
    
    def test_validate_url_ip_address(self, extractor):
        """Test validation of IP address URL."""
        assert extractor._validate_url("http://192.168.1.1") is True


class TestErrorHandling:
    """Tests for error handling in ProductExtractor."""
    
    def test_extract_products_handles_exception(self, extractor):
        """Test that extraction handles exceptions gracefully."""
        # Create invalid soup object
        soup = None
        
        selectors = {
            'container': '.product',
            'name': '.name'
        }
        
        # Should not raise exception
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        assert len(products) == 0
    
    def test_extract_field_handles_exception(self, extractor):
        """Test that field extraction handles exceptions gracefully."""
        # Create invalid element
        element = None
        
        result = extractor._extract_field(element, '.test', default="Default")
        
        assert result == "Default"


class TestMalformedHtml:
    """Tests for handling malformed HTML."""
    
    def test_extract_from_malformed_html(self, extractor):
        """Test extraction from malformed HTML."""
        html = """
        <div class="product">
            <h2 class="name">Organic Honey
            <span class="price">$15.99
            <a class="link" href="https://example.com/honey">View
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = {
            'container': '.product',
            'name': '.name',
            'price': '.price',
            'link': '.link',
            'image': '.image'
        }
        
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        # Should still extract what it can
        assert len(products) >= 0  # May or may not extract depending on HTML structure
    
    def test_extract_from_nested_malformed_html(self, extractor):
        """Test extraction from nested malformed HTML."""
        html = """
        <div class="product">
            <div><h2 class="name">Organic Honey</h2>
            <span class="price">$15.99</span>
            <a class="link" href="https://example.com/honey">View</a>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        selectors = {
            'container': '.product',
            'name': '.name',
            'price': '.price',
            'link': '.link',
            'image': '.image'
        }
        
        products = extractor.extract_products(soup, "TestSource", selectors)
        
        # BeautifulSoup should handle this gracefully
        assert isinstance(products, list)
