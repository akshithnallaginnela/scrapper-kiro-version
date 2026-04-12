"""Main orchestrator for the Organic Products Web Scraper.

This module coordinates all components to execute the complete scraping workflow:
1. Load configuration
2. Initialize logging
3. Initialize scraper components
4. Execute scraping workflow
5. Generate output files
6. Handle errors and cleanup
"""

import sys
import time
from datetime import datetime
from typing import Dict, List
from pathlib import Path

# Handle both module and script execution
try:
    from src.config_manager import ConfigurationManager
    from src.logger import setup_logger
    from src.source_manager import SourceManager
    from src.product_extractor import ProductExtractor
    from src.data_aggregator import DataAggregator
    from src.trend_analyzer import TrendAnalyzer
    from src.output_formatter import OutputFormatter
    from src.performance_monitor import PerformanceMonitor
    from src.models import ProductRecord, OutputMetadata, ScrapingResult
except ImportError:
    # Running as script, add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.config_manager import ConfigurationManager
    from src.logger import setup_logger
    from src.source_manager import SourceManager
    from src.product_extractor import ProductExtractor
    from src.data_aggregator import DataAggregator
    from src.trend_analyzer import TrendAnalyzer
    from src.output_formatter import OutputFormatter
    from src.performance_monitor import PerformanceMonitor
    from src.models import ProductRecord, OutputMetadata, ScrapingResult

from bs4 import BeautifulSoup


class InsufficientDataException(Exception):
    """Exception raised when fewer than 2 sources are successfully scraped."""
    pass


def main(config_path: str = None) -> int:
    """
    Main orchestration function that coordinates all scraper components.
    
    Workflow:
    1. Initialize Configuration Manager and load config
    2. Initialize logging system
    3. Initialize all scraper components
    4. Execute scraping workflow:
       - Source Manager → scrape all sources
       - Product Extractor → extract products from HTML
       - Data Aggregator → combine and deduplicate products
       - Trend Analyzer → calculate scores and rank products
       - Output Formatter → generate JSON and CSV files
    5. Track scraping duration and metadata
    6. Handle InsufficientDataException when fewer than 2 sources succeed
    7. Implement graceful shutdown and cleanup
    
    Args:
        config_path: Path to configuration file (JSON or YAML)
                    If None, uses default configuration
    
    Returns:
        Exit code: 0 for success, 1 for failure
        
    Requirements:
        - 1.1: Multi-source data collection
        - 1.2: B2C platform scraping
        - 1.3: B2B marketplace scraping
        - 1.4: Specialized organic product websites
        - 1.5: Social media trend data
        - 6.4: Insufficient data handling
    """
    logger = None
    source_manager = None
    performance_monitor = None
    start_time = time.time()
    
    try:
        # Step 1: Initialize Configuration Manager
        print("Initializing Organic Products Web Scraper...")
        config_manager = ConfigurationManager(config_path=config_path)
        
        # Step 2: Initialize logging system
        logger = setup_logger(
            name="organic_scraper",
            log_file=config_manager.get_log_file(),
            log_level=config_manager.get_log_level(),
            max_log_size_mb=config_manager.get_max_log_size_mb()
        )
        
        # Initialize performance monitor
        performance_monitor = PerformanceMonitor(
            memory_limit_mb=500.0,  # Requirement 12.5
            logger=logger
        )
        
        logger.info("=" * 80)
        logger.info("Organic Products Web Scraper - Starting")
        logger.info("=" * 80)
        logger.info(f"Configuration loaded from: {config_path or 'defaults'}")
        logger.info(f"Output directory: {config_manager.get_output_directory()}")
        logger.info(f"Log level: {config_manager.get_log_level()}")
        
        # Log initial memory usage
        performance_monitor.log_memory_usage("Initialization")
        
        # Step 3: Initialize all scraper components
        logger.info("Initializing scraper components...")
        
        source_manager = SourceManager(
            config=config_manager,
            logger=logger
        )
        
        product_extractor = ProductExtractor(logger=logger)
        data_aggregator = DataAggregator(logger=logger)
        trend_analyzer = TrendAnalyzer(logger=logger)
        output_formatter = OutputFormatter(
            output_dir=config_manager.get_output_directory(),
            logger=logger
        )
        
        logger.info("All components initialized successfully")
        
        # Check memory after initialization
        performance_monitor.log_memory_usage("After component initialization")
        
        # Step 4: Execute scraping workflow
        logger.info("Starting scraping workflow...")
        
        # 4.1: Source Manager - Scrape all sources
        logger.info("Phase 1: Scraping sources...")
        scraping_results = source_manager.scrape_all_sources()
        
        # Check memory after scraping
        performance_monitor.log_memory_usage("After scraping sources")
        
        # Check if sufficient sources succeeded
        successful_results = [r for r in scraping_results if r.success]
        failed_results = [r for r in scraping_results if not r.success]
        
        logger.info(
            f"Scraping phase complete: "
            f"{len(successful_results)} successful, "
            f"{len(failed_results)} failed"
        )
        
        # Requirement 6.4: Handle insufficient data
        if len(successful_results) < 2:
            failed_sources = [r.source_name for r in failed_results]
            error_details = [
                f"{r.source_name}: {r.error_message}" 
                for r in failed_results
            ]
            
            error_message = (
                f"Insufficient data: Only {len(successful_results)} source(s) "
                f"successfully scraped (minimum 2 required).\n"
                f"Failed sources: {', '.join(failed_sources)}\n"
                f"Details:\n" + "\n".join(f"  - {detail}" for detail in error_details)
            )
            
            logger.error(error_message)
            raise InsufficientDataException(error_message)
        
        # 4.2: Product Extractor - Extract products from HTML
        logger.info("Phase 2: Extracting products from HTML...")
        products_by_source: Dict[str, List[ProductRecord]] = {}
        
        for result in successful_results:
            try:
                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(result.html_content, 'html.parser', from_encoding='utf-8')
                
                # Get selectors for this source
                source_config = _find_source_config(
                    config_manager.get_sources(),
                    result.source_name
                )
                
                if source_config and 'selectors' in source_config:
                    selectors = source_config['selectors']
                else:
                    # Use default selectors if not specified
                    logger.warning(
                        f"No selectors configured for {result.source_name}, "
                        f"using defaults"
                    )
                    selectors = {
                        'container': 'div.product',
                        'name': 'h2',
                        'price': '.price',
                        'link': 'a',
                        'image': 'img'
                    }
                
                # Extract products
                products = product_extractor.extract_products(
                    soup=soup,
                    source_name=result.source_name,
                    selectors=selectors
                )
                
                products_by_source[result.source_name] = products
                
                logger.info(
                    f"Extracted {len(products)} products from {result.source_name}"
                )
                
            except Exception as e:
                logger.error(
                    f"Error extracting products from {result.source_name}: {e}"
                )
                products_by_source[result.source_name] = []
        
        # 4.3: Data Aggregator - Combine and deduplicate
        logger.info("Phase 3: Aggregating and deduplicating products...")
        aggregated_products = data_aggregator.aggregate(products_by_source)
        
        # Check memory after aggregation
        performance_monitor.log_memory_usage("After data aggregation")
        
        logger.info(f"Aggregation complete: {len(aggregated_products)} unique products")
        
        # Check if we have any products
        if not aggregated_products:
            logger.warning("No products extracted from any source")
            logger.info("Scraping completed with no results")
            return 0
        
        # 4.4: Trend Analyzer - Calculate scores and rank
        logger.info("Phase 4: Analyzing trends and ranking products...")
        scored_products = trend_analyzer.calculate_trending_scores(aggregated_products)
        ranked_products = trend_analyzer.rank_products(scored_products)
        top_products = trend_analyzer.get_top_n(ranked_products, n=5)
        
        logger.info(f"Trend analysis complete: Top {len(top_products)} products identified")
        
        # 4.5: Output Formatter - Generate output files
        logger.info("Phase 5: Generating output files...")
        
        # Prepare metadata
        end_time = time.time()
        duration = end_time - start_time
        
        metadata = {
            'collection_timestamp': datetime.now(),
            'total_sources_configured': len(config_manager.get_sources()),
            'sources_successfully_scraped': [r.source_name for r in successful_results],
            'sources_failed': [r.source_name for r in failed_results],
            'total_products_found': len(aggregated_products),
            'top_products_count': len(top_products),
            'scraping_duration_seconds': round(duration, 2),
            'version': '1.0.0'
        }
        
        # Write output files
        json_filename = output_formatter.write_json(top_products, metadata)
        csv_filename = output_formatter.write_csv(top_products, metadata)
        
        logger.info(f"Output files generated:")
        logger.info(f"  - JSON: {json_filename}")
        logger.info(f"  - CSV: {csv_filename}")
        
        # Step 5: Success summary
        logger.info("=" * 80)
        logger.info("Scraping completed successfully!")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Sources scraped: {len(successful_results)}/{len(scraping_results)}")
        logger.info(f"Products found: {len(aggregated_products)}")
        logger.info(f"Top products: {len(top_products)}")
        
        # Log final performance metrics
        final_metrics = performance_monitor.get_metrics(execution_time=duration)
        performance_monitor.log_metrics(final_metrics, "Final")
        
        # Verify performance requirements
        if not final_metrics.is_within_memory_limit():
            logger.warning(
                f"Memory limit exceeded: {final_metrics.memory_usage_mb:.2f} MB "
                f"(limit: {final_metrics.memory_limit_mb:.2f} MB)"
            )
        
        if duration > 300:  # 5 minutes
            logger.warning(
                f"Execution time exceeded 5 minutes: {duration:.2f}s"
            )
        
        logger.info("=" * 80)
        
        print(f"\nScraping completed successfully!")
        print(f"Results saved to:")
        print(f"  - {config_manager.get_output_directory()}/{json_filename}")
        print(f"  - {config_manager.get_output_directory()}/{csv_filename}")
        
        return 0
        
    except InsufficientDataException as e:
        # Handle insufficient data gracefully
        if logger:
            logger.error(f"Scraping failed: {e}")
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        
        return 1
        
    except KeyboardInterrupt:
        # Handle user interruption
        if logger:
            logger.warning("Scraping interrupted by user")
        else:
            print("\nScraping interrupted by user", file=sys.stderr)
        
        return 1
        
    except Exception as e:
        # Handle unexpected errors
        if logger:
            logger.exception(f"Unexpected error during scraping: {e}")
        else:
            print(f"ERROR: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
        
        return 1
        
    finally:
        # Step 6: Graceful shutdown and cleanup
        if logger:
            logger.info("Performing cleanup...")
        
        # Close source manager (closes scrapers)
        if source_manager:
            try:
                source_manager.close()
                if logger:
                    logger.info("Source manager closed")
            except Exception as e:
                if logger:
                    logger.warning(f"Error closing source manager: {e}")
        
        if logger:
            logger.info("Cleanup complete")
            logger.info("Organic Products Web Scraper - Finished")


def _find_source_config(sources: List[Dict], source_name: str) -> Dict:
    """
    Find source configuration by name.
    
    Args:
        sources: List of source configuration dictionaries
        source_name: Name of source to find
        
    Returns:
        Source configuration dictionary or None if not found
    """
    for source in sources:
        if source.get('name') == source_name:
            return source
    return None


if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Organic Products Web Scraper - Identify top trending organic products"
    )
    parser.add_argument(
        '--config',
        '-c',
        type=str,
        default=None,
        help='Path to configuration file (JSON or YAML)'
    )
    
    args = parser.parse_args()
    
    # Run main function
    exit_code = main(config_path=args.config)
    sys.exit(exit_code)
