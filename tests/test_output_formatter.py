"""Unit tests for the OutputFormatter."""

import json
import csv
import os
import tempfile
from datetime import datetime
from pathlib import Path
import pytest

from src.output_formatter import OutputFormatter
from src.models import ProductRecord
from src.logger import setup_logger


def cleanup_logger(logger):
    """Helper function to cleanup logger handlers."""
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


class TestOutputFormatter:
    """Test cases for the OutputFormatter class."""
    
    def test_init_creates_output_directory(self):
        """Test that __init__ creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "output", "subdir")
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(name="test_formatter_1", log_file=log_file)
            
            try:
                formatter = OutputFormatter(output_dir, logger)
                
                # Check that directory was created
                assert os.path.exists(output_dir)
                assert os.path.isdir(output_dir)
            finally:
                cleanup_logger(logger)
    
    def test_generate_filename_includes_timestamp(self):
        """Test that _generate_filename includes timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(name="test_formatter_2", log_file=log_file)
            
            try:
                formatter = OutputFormatter(tmpdir, logger)
                
                # Generate filename
                filename = formatter._generate_filename("json")
                
                # Check format: organic_products_YYYYMMDD_HHMMSS.json
                assert filename.startswith("organic_products_")
                assert filename.endswith(".json")
                assert len(filename) == len("organic_products_20240101_120000.json")
            finally:
                cleanup_logger(logger)
    
    def test_write_json_creates_file(self):
        """Test that write_json creates a JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(name="test_formatter_3", log_file=log_file)
            
            try:
                formatter = OutputFormatter(tmpdir, logger)
                
                # Create test products
                products = [
                    ProductRecord(
                        name="Organic Honey",
                        price="$15.99",
                        source="Amazon",
                        link="https://amazon.com/product1",
                        image_url="https://amazon.com/image1.jpg",
                        timestamp=datetime(2024, 1, 1, 12, 0, 0),
                        mentions=2,
                        sources_list=["Amazon", "Flipkart"]
                    )
                ]
                
                metadata = {
                    "collection_timestamp": datetime(2024, 1, 1, 12, 0, 0),
                    "total_sources_configured": 5,
                    "sources_successfully_scraped": ["Amazon", "Flipkart"],
                    "sources_failed": [],
                    "total_products_found": 1,
                    "top_products_count": 1,
                    "scraping_duration_seconds": 10.5
                }
                
                # Write JSON
                filename = formatter.write_json(products, metadata)
                
                # Check that file was created
                filepath = os.path.join(tmpdir, filename)
                assert os.path.exists(filepath)
                
                # Check file content
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    assert "metadata" in data
                    assert "products" in data
                    assert len(data["products"]) == 1
                    assert data["products"][0]["name"] == "Organic Honey"
            finally:
                cleanup_logger(logger)
    
    def test_write_csv_creates_file(self):
        """Test that write_csv creates a CSV file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(name="test_formatter_4", log_file=log_file)
            
            try:
                formatter = OutputFormatter(tmpdir, logger)
                
                # Create test products
                products = [
                    ProductRecord(
                        name="Organic Honey",
                        price="$15.99",
                        source="Amazon",
                        link="https://amazon.com/product1",
                        image_url="https://amazon.com/image1.jpg",
                        timestamp=datetime(2024, 1, 1, 12, 0, 0),
                        mentions=2,
                        sources_list=["Amazon", "Flipkart"]
                    )
                ]
                
                metadata = {}
                
                # Write CSV
                filename = formatter.write_csv(products, metadata)
                
                # Check that file was created
                filepath = os.path.join(tmpdir, filename)
                assert os.path.exists(filepath)
                
                # Check file content
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    assert len(rows) == 1
                    assert rows[0]["name"] == "Organic Honey"
                    assert rows[0]["price"] == "$15.99"
            finally:
                cleanup_logger(logger)
    
    def test_json_includes_all_fields(self):
        """Test that JSON output includes all product fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(name="test_formatter_5", log_file=log_file)
            
            try:
                formatter = OutputFormatter(tmpdir, logger)
                
                products = [
                    ProductRecord(
                        name="Organic Tea",
                        price="$12.50",
                        source="Flipkart",
                        link="https://flipkart.com/product2",
                        image_url="https://flipkart.com/image2.jpg",
                        timestamp=datetime(2024, 1, 2, 14, 30, 0),
                        mentions=3,
                        sources_list=["Amazon", "Flipkart", "Organic Store"]
                    )
                ]
                
                metadata = {"test": "value"}
                filename = formatter.write_json(products, metadata)
                
                filepath = os.path.join(tmpdir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    product = data["products"][0]
                    
                    # Check all fields are present
                    assert "name" in product
                    assert "price" in product
                    assert "source" in product
                    assert "link" in product
                    assert "image_url" in product
                    assert "timestamp" in product
                    assert "mentions" in product
                    assert "sources_list" in product
            finally:
                cleanup_logger(logger)
    
    def test_csv_includes_header_row(self):
        """Test that CSV output includes header row with field names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(name="test_formatter_6", log_file=log_file)
            
            try:
                formatter = OutputFormatter(tmpdir, logger)
                
                products = [
                    ProductRecord(
                        name="Organic Coffee",
                        price="$18.00",
                        source="Amazon",
                        link="https://amazon.com/product3",
                        image_url="https://amazon.com/image3.jpg",
                        timestamp=datetime(2024, 1, 3, 10, 0, 0),
                        mentions=1,
                        sources_list=["Amazon"]
                    )
                ]
                
                metadata = {}
                filename = formatter.write_csv(products, metadata)
                
                filepath = os.path.join(tmpdir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    
                    # Check header row
                    assert "name" in header
                    assert "price" in header
                    assert "source" in header
                    assert "link" in header
                    assert "image_url" in header
                    assert "timestamp" in header
                    assert "mentions" in header
                    assert "sources_list" in header
            finally:
                cleanup_logger(logger)
    
    def test_json_serializes_datetime_objects(self):
        """Test that JSON properly serializes datetime objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(name="test_formatter_7", log_file=log_file)
            
            try:
                formatter = OutputFormatter(tmpdir, logger)
                
                test_datetime = datetime(2024, 1, 15, 9, 30, 45)
                products = [
                    ProductRecord(
                        name="Organic Milk",
                        price="$5.99",
                        source="Organic Store",
                        link="https://organicstore.com/milk",
                        image_url="https://organicstore.com/milk.jpg",
                        timestamp=test_datetime,
                        mentions=1,
                        sources_list=["Organic Store"]
                    )
                ]
                
                metadata = {
                    "collection_timestamp": test_datetime
                }
                
                filename = formatter.write_json(products, metadata)
                
                filepath = os.path.join(tmpdir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Check datetime is serialized as ISO format string
                    assert isinstance(data["products"][0]["timestamp"], str)
                    assert "2024-01-15" in data["products"][0]["timestamp"]
                    assert isinstance(data["metadata"]["collection_timestamp"], str)
            finally:
                cleanup_logger(logger)
    
    def test_write_multiple_products(self):
        """Test writing multiple products to both JSON and CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger(name="test_formatter_8", log_file=log_file)
            
            try:
                formatter = OutputFormatter(tmpdir, logger)
                
                products = [
                    ProductRecord(
                        name="Product 1",
                        price="$10.00",
                        source="Source 1",
                        link="https://example.com/1",
                        image_url="https://example.com/img1.jpg",
                        timestamp=datetime(2024, 1, 1, 12, 0, 0),
                        mentions=1,
                        sources_list=["Source 1"]
                    ),
                    ProductRecord(
                        name="Product 2",
                        price="$20.00",
                        source="Source 2",
                        link="https://example.com/2",
                        image_url="https://example.com/img2.jpg",
                        timestamp=datetime(2024, 1, 2, 12, 0, 0),
                        mentions=2,
                        sources_list=["Source 1", "Source 2"]
                    ),
                    ProductRecord(
                        name="Product 3",
                        price="Not Available",
                        source="Source 3",
                        link="https://example.com/3",
                        image_url="Not Available",
                        timestamp=datetime(2024, 1, 3, 12, 0, 0),
                        mentions=1,
                        sources_list=["Source 3"]
                    )
                ]
                
                metadata = {}
                
                # Write JSON
                json_filename = formatter.write_json(products, metadata)
                json_filepath = os.path.join(tmpdir, json_filename)
                with open(json_filepath, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    assert len(json_data["products"]) == 3
                
                # Write CSV
                csv_filename = formatter.write_csv(products, metadata)
                csv_filepath = os.path.join(tmpdir, csv_filename)
                with open(csv_filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    csv_rows = list(reader)
                    assert len(csv_rows) == 3
            finally:
                cleanup_logger(logger)
