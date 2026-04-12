"""Output formatting and file writing for the Organic Products Web Scraper."""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from logging import Logger

from src.models import ProductRecord, OutputMetadata


class OutputFormatter:
    """Formats and writes output files."""
    
    def __init__(self, output_dir: str, logger: Logger):
        """
        Initialize with output directory and logger.
        
        Args:
            output_dir: Path to output directory
            logger: Logger instance for logging operations
        """
        self.output_dir = Path(output_dir)
        self.logger = logger
        self._ensure_output_directory()
    
    def _ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Output directory ensured: {self.output_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create output directory {self.output_dir}: {e}")
            raise
    
    def _generate_filename(self, extension: str) -> str:
        """
        Generate filename with timestamp.
        
        Args:
            extension: File extension (e.g., 'json', 'csv')
            
        Returns:
            Filename string with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"organic_products_{timestamp}.{extension}"
    
    def write_json(
        self, 
        products: List[ProductRecord], 
        metadata: Dict[str, Any]
    ) -> str:
        """
        Write products to JSON file.
        
        Args:
            products: List of ProductRecord objects
            metadata: Metadata dictionary to include in output
            
        Returns:
            Filename of created JSON file
        """
        filename = self._generate_filename("json")
        filepath = self.output_dir / filename
        
        try:
            # Convert products to dictionaries
            products_data = []
            for product in products:
                product_dict = {
                    "name": product.name,
                    "price": product.price,
                    "source": product.source,
                    "link": product.link,
                    "image_url": product.image_url,
                    "timestamp": product.timestamp.isoformat(),
                    "mentions": product.mentions,
                    "sources_list": product.sources_list
                }
                products_data.append(product_dict)
            
            # Prepare output structure
            output_data = {
                "metadata": self._serialize_metadata(metadata),
                "products": products_data
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
            
            self.logger.info(f"JSON output written to {filepath}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to write JSON file {filepath}: {e}")
            raise
    
    def write_csv(
        self, 
        products: List[ProductRecord], 
        metadata: Dict[str, Any]
    ) -> str:
        """
        Write products to CSV file.
        
        Args:
            products: List of ProductRecord objects
            metadata: Metadata dictionary to include in output
            
        Returns:
            Filename of created CSV file
        """
        filename = self._generate_filename("csv")
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                # Define CSV header row with field names
                fieldnames = [
                    'name', 
                    'price', 
                    'source', 
                    'link', 
                    'image_url', 
                    'timestamp', 
                    'mentions', 
                    'sources_list'
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write product rows
                for product in products:
                    row = {
                        'name': product.name,
                        'price': product.price,
                        'source': product.source,
                        'link': product.link,
                        'image_url': product.image_url,
                        'timestamp': product.timestamp.isoformat(),
                        'mentions': product.mentions,
                        'sources_list': ', '.join(product.sources_list) if product.sources_list else ''
                    }
                    writer.writerow(row)
            
            self.logger.info(f"CSV output written to {filepath}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to write CSV file {filepath}: {e}")
            raise
    
    def _json_serializer(self, obj: Any) -> str:
        """
        Custom JSON serializer for datetime objects.
        
        Args:
            obj: Object to serialize
            
        Returns:
            Serialized string representation
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _serialize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize metadata dictionary, handling datetime objects.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Serialized metadata dictionary
        """
        serialized = {}
        for key, value in metadata.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, list):
                serialized[key] = value
            else:
                serialized[key] = value
        return serialized
