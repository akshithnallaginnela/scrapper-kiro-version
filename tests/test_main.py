"""Unit tests for the main orchestrator."""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from pathlib import Path

from src.main import main, InsufficientDataException, _find_source_config
from src.models import ScrapingResult, ProductRecord


class TestInsufficientDataException:
    """Test InsufficientDataException."""
    
    def test_exception_creation(self):
        """Test that InsufficientDataException can be created and raised."""
        with pytest.raises(InsufficientDataException) as exc_info:
            raise InsufficientDataException("Test error message")
        
        assert "Test error message" in str(exc_info.value)


class TestFindSourceConfig:
    """Test _find_source_config helper function."""
    
    def test_find_existing_source(self):
        """Test finding an existing source configuration."""
        sources = [
            {'name': 'Source1', 'url': 'http://example1.com'},
            {'name': 'Source2', 'url': 'http://example2.com'},
            {'name': 'Source3', 'url': 'http://example3.com'}
        ]
        
        result = _find_source_config(sources, 'Source2')
        
        assert result is not None
        assert result['name'] == 'Source2'
        assert result['url'] == 'http://example2.com'
    
    def test_find_nonexistent_source(self):
        """Test finding a source that doesn't exist."""
        sources = [
            {'name': 'Source1', 'url': 'http://example1.com'},
            {'name': 'Source2', 'url': 'http://example2.com'}
        ]
        
        result = _find_source_config(sources, 'NonExistent')
        
        assert result is None
    
    def test_find_in_empty_list(self):
        """Test finding in an empty source list."""
        sources = []
        
        result = _find_source_config(sources, 'AnySource')
        
        assert result is None


class TestMainOrchestrator:
    """Test main orchestrator function."""
    
    @patch('src.main.OutputFormatter')
    @patch('src.main.TrendAnalyzer')
    @patch('src.main.DataAggregator')
    @patch('src.main.ProductExtractor')
    @patch('src.main.SourceManager')
    @patch('src.main.setup_logger')
    @patch('src.main.ConfigurationManager')
    def test_successful_scraping_workflow(
        self,
        mock_config_cls,
        mock_logger_setup,
        mock_source_mgr_cls,
        mock_extractor_cls,
        mock_aggregator_cls,
        mock_analyzer_cls,
        mock_formatter_cls
    ):
        """Test successful end-to-end scraping workflow."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get_sources.return_value = [
            {'name': 'Source1', 'url': 'http://example1.com', 'selectors': {}},
            {'name': 'Source2', 'url': 'http://example2.com', 'selectors': {}}
        ]
        mock_config.get_log_file.return_value = 'test.log'
        mock_config.get_log_level.return_value = 'INFO'
        mock_config.get_max_log_size_mb.return_value = 10
        mock_config.get_output_directory.return_value = './output'
        mock_config_cls.return_value = mock_config
        
        mock_logger = Mock()
        mock_logger_setup.return_value = mock_logger
        
        # Mock scraping results (2 successful)
        mock_source_mgr = Mock()
        mock_source_mgr.scrape_all_sources.return_value = [
            ScrapingResult(
                source_name='Source1',
                success=True,
                html_content='<html><body>Product 1</body></html>',
                response_time=1.0
            ),
            ScrapingResult(
                source_name='Source2',
                success=True,
                html_content='<html><body>Product 2</body></html>',
                response_time=1.5
            )
        ]
        mock_source_mgr_cls.return_value = mock_source_mgr
        
        # Mock product extraction
        mock_extractor = Mock()
        mock_product1 = ProductRecord(
            name='Organic Honey',
            price='$10',
            source='Source1',
            link='http://example.com/1',
            image_url='http://example.com/img1.jpg',
            timestamp=datetime.now(),
            mentions=1,
            sources_list=['Source1']
        )
        mock_product2 = ProductRecord(
            name='Organic Tea',
            price='$15',
            source='Source2',
            link='http://example.com/2',
            image_url='http://example.com/img2.jpg',
            timestamp=datetime.now(),
            mentions=1,
            sources_list=['Source2']
        )
        mock_extractor.extract_products.side_effect = [
            [mock_product1],
            [mock_product2]
        ]
        mock_extractor_cls.return_value = mock_extractor
        
        # Mock aggregation
        mock_aggregator = Mock()
        mock_aggregator.aggregate.return_value = [mock_product1, mock_product2]
        mock_aggregator_cls.return_value = mock_aggregator
        
        # Mock trend analysis
        mock_analyzer = Mock()
        mock_analyzer.calculate_trending_scores.return_value = [
            (mock_product1, 0.8),
            (mock_product2, 0.7)
        ]
        mock_analyzer.rank_products.return_value = [mock_product1, mock_product2]
        mock_analyzer.get_top_n.return_value = [mock_product1, mock_product2]
        mock_analyzer_cls.return_value = mock_analyzer
        
        # Mock output formatting
        mock_formatter = Mock()
        mock_formatter.write_json.return_value = 'output.json'
        mock_formatter.write_csv.return_value = 'output.csv'
        mock_formatter_cls.return_value = mock_formatter
        
        # Execute main
        exit_code = main(config_path='test_config.json')
        
        # Assertions
        assert exit_code == 0
        
        # Verify component initialization
        mock_config_cls.assert_called_once_with(config_path='test_config.json')
        mock_logger_setup.assert_called_once()
        mock_source_mgr_cls.assert_called_once()
        mock_extractor_cls.assert_called_once()
        mock_aggregator_cls.assert_called_once()
        mock_analyzer_cls.assert_called_once()
        mock_formatter_cls.assert_called_once()
        
        # Verify workflow execution
        mock_source_mgr.scrape_all_sources.assert_called_once()
        assert mock_extractor.extract_products.call_count == 2
        mock_aggregator.aggregate.assert_called_once()
        mock_analyzer.calculate_trending_scores.assert_called_once()
        mock_analyzer.rank_products.assert_called_once()
        mock_analyzer.get_top_n.assert_called_once_with([mock_product1, mock_product2], n=5)
        mock_formatter.write_json.assert_called_once()
        mock_formatter.write_csv.assert_called_once()
        
        # Verify cleanup
        mock_source_mgr.close.assert_called_once()
    
    @patch('src.main.SourceManager')
    @patch('src.main.setup_logger')
    @patch('src.main.ConfigurationManager')
    def test_insufficient_data_exception(
        self,
        mock_config_cls,
        mock_logger_setup,
        mock_source_mgr_cls
    ):
        """Test that InsufficientDataException is raised when fewer than 2 sources succeed."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get_sources.return_value = [
            {'name': 'Source1', 'url': 'http://example1.com'},
            {'name': 'Source2', 'url': 'http://example2.com'}
        ]
        mock_config.get_log_file.return_value = 'test.log'
        mock_config.get_log_level.return_value = 'INFO'
        mock_config.get_max_log_size_mb.return_value = 10
        mock_config.get_output_directory.return_value = './output'
        mock_config_cls.return_value = mock_config
        
        mock_logger = Mock()
        mock_logger_setup.return_value = mock_logger
        
        # Mock scraping results (only 1 successful)
        mock_source_mgr = Mock()
        mock_source_mgr.scrape_all_sources.return_value = [
            ScrapingResult(
                source_name='Source1',
                success=True,
                html_content='<html><body>Product 1</body></html>',
                response_time=1.0
            ),
            ScrapingResult(
                source_name='Source2',
                success=False,
                error_message='Connection timeout',
                response_time=30.0
            )
        ]
        mock_source_mgr_cls.return_value = mock_source_mgr
        
        # Execute main
        exit_code = main(config_path='test_config.json')
        
        # Should return error code
        assert exit_code == 1
        
        # Verify error was logged
        mock_logger.error.assert_called()
        error_call_args = str(mock_logger.error.call_args)
        assert 'Insufficient data' in error_call_args
        
        # Verify cleanup still happens
        mock_source_mgr.close.assert_called_once()
    
    @patch('src.main.SourceManager')
    @patch('src.main.setup_logger')
    @patch('src.main.ConfigurationManager')
    def test_no_products_extracted(
        self,
        mock_config_cls,
        mock_logger_setup,
        mock_source_mgr_cls
    ):
        """Test handling when no products are extracted from any source."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get_sources.return_value = [
            {'name': 'Source1', 'url': 'http://example1.com', 'selectors': {}},
            {'name': 'Source2', 'url': 'http://example2.com', 'selectors': {}}
        ]
        mock_config.get_log_file.return_value = 'test.log'
        mock_config.get_log_level.return_value = 'INFO'
        mock_config.get_max_log_size_mb.return_value = 10
        mock_config.get_output_directory.return_value = './output'
        mock_config_cls.return_value = mock_config
        
        mock_logger = Mock()
        mock_logger_setup.return_value = mock_logger
        
        # Mock scraping results (2 successful but no products)
        mock_source_mgr = Mock()
        mock_source_mgr.scrape_all_sources.return_value = [
            ScrapingResult(
                source_name='Source1',
                success=True,
                html_content='<html><body></body></html>',
                response_time=1.0
            ),
            ScrapingResult(
                source_name='Source2',
                success=True,
                html_content='<html><body></body></html>',
                response_time=1.5
            )
        ]
        mock_source_mgr_cls.return_value = mock_source_mgr
        
        # Execute main with mocked components
        with patch('src.main.ProductExtractor') as mock_extractor_cls, \
             patch('src.main.DataAggregator') as mock_aggregator_cls:
            
            mock_extractor = Mock()
            mock_extractor.extract_products.return_value = []
            mock_extractor_cls.return_value = mock_extractor
            
            mock_aggregator = Mock()
            mock_aggregator.aggregate.return_value = []
            mock_aggregator_cls.return_value = mock_aggregator
            
            exit_code = main(config_path='test_config.json')
        
        # Should return success (0) but with warning
        assert exit_code == 0
        
        # Verify warning was logged
        mock_logger.warning.assert_any_call('No products extracted from any source')
        
        # Verify cleanup
        mock_source_mgr.close.assert_called_once()
    
    @patch('src.main.SourceManager')
    @patch('src.main.setup_logger')
    @patch('src.main.ConfigurationManager')
    def test_keyboard_interrupt_handling(
        self,
        mock_config_cls,
        mock_logger_setup,
        mock_source_mgr_cls
    ):
        """Test graceful handling of keyboard interrupt."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get_sources.return_value = []
        mock_config.get_log_file.return_value = 'test.log'
        mock_config.get_log_level.return_value = 'INFO'
        mock_config.get_max_log_size_mb.return_value = 10
        mock_config.get_output_directory.return_value = './output'
        mock_config_cls.return_value = mock_config
        
        mock_logger = Mock()
        mock_logger_setup.return_value = mock_logger
        
        # Mock source manager to raise KeyboardInterrupt
        mock_source_mgr = Mock()
        mock_source_mgr.scrape_all_sources.side_effect = KeyboardInterrupt()
        mock_source_mgr_cls.return_value = mock_source_mgr
        
        # Execute main
        exit_code = main(config_path='test_config.json')
        
        # Should return error code
        assert exit_code == 1
        
        # Verify warning was logged
        mock_logger.warning.assert_called_with('Scraping interrupted by user')
        
        # Verify cleanup
        mock_source_mgr.close.assert_called_once()
    
    @patch('src.main.SourceManager')
    @patch('src.main.setup_logger')
    @patch('src.main.ConfigurationManager')
    def test_unexpected_exception_handling(
        self,
        mock_config_cls,
        mock_logger_setup,
        mock_source_mgr_cls
    ):
        """Test handling of unexpected exceptions."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get_sources.return_value = []
        mock_config.get_log_file.return_value = 'test.log'
        mock_config.get_log_level.return_value = 'INFO'
        mock_config.get_max_log_size_mb.return_value = 10
        mock_config.get_output_directory.return_value = './output'
        mock_config_cls.return_value = mock_config
        
        mock_logger = Mock()
        mock_logger_setup.return_value = mock_logger
        
        # Mock source manager to raise unexpected exception
        mock_source_mgr = Mock()
        mock_source_mgr.scrape_all_sources.side_effect = RuntimeError("Unexpected error")
        mock_source_mgr_cls.return_value = mock_source_mgr
        
        # Execute main
        exit_code = main(config_path='test_config.json')
        
        # Should return error code
        assert exit_code == 1
        
        # Verify exception was logged
        mock_logger.exception.assert_called()
        
        # Verify cleanup
        mock_source_mgr.close.assert_called_once()
    
    @patch('src.main.setup_logger')
    @patch('src.main.ConfigurationManager')
    def test_cleanup_on_source_manager_close_error(
        self,
        mock_config_cls,
        mock_logger_setup
    ):
        """Test that cleanup continues even if source manager close fails."""
        # Setup mocks
        mock_config = Mock()
        mock_config.get_sources.return_value = []
        mock_config.get_log_file.return_value = 'test.log'
        mock_config.get_log_level.return_value = 'INFO'
        mock_config.get_max_log_size_mb.return_value = 10
        mock_config.get_output_directory.return_value = './output'
        mock_config_cls.return_value = mock_config
        
        mock_logger = Mock()
        mock_logger_setup.return_value = mock_logger
        
        with patch('src.main.SourceManager') as mock_source_mgr_cls:
            mock_source_mgr = Mock()
            mock_source_mgr.scrape_all_sources.side_effect = RuntimeError("Test error")
            mock_source_mgr.close.side_effect = Exception("Close error")
            mock_source_mgr_cls.return_value = mock_source_mgr
            
            # Execute main
            exit_code = main(config_path='test_config.json')
        
        # Should still return error code
        assert exit_code == 1
        
        # Verify close was attempted
        mock_source_mgr.close.assert_called_once()
        
        # Verify warning about close error was logged
        mock_logger.warning.assert_any_call('Error closing source manager: Close error')
