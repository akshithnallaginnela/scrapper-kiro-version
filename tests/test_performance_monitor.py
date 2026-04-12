"""Unit tests for PerformanceMonitor class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import psutil

from src.performance_monitor import PerformanceMonitor, PerformanceMetrics


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return Mock()


@pytest.fixture
def mock_process():
    """Create mock psutil.Process."""
    process = Mock()
    process.memory_info.return_value = Mock(rss=100 * 1024 * 1024)  # 100 MB
    process.memory_percent.return_value = 5.0
    process.cpu_percent.return_value = 10.0
    return process


@pytest.fixture
def performance_monitor(mock_logger, mock_process):
    """Create PerformanceMonitor instance with mocked dependencies."""
    with patch('src.performance_monitor.psutil.Process', return_value=mock_process):
        monitor = PerformanceMonitor(memory_limit_mb=500.0, logger=mock_logger)
        return monitor


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics dataclass."""
    
    def test_metrics_creation(self):
        """Test creating PerformanceMetrics instance."""
        metrics = PerformanceMetrics(
            memory_usage_mb=250.0,
            memory_percent=10.0,
            cpu_percent=25.0,
            execution_time_seconds=120.0,
            memory_limit_mb=500.0
        )
        
        assert metrics.memory_usage_mb == 250.0
        assert metrics.memory_percent == 10.0
        assert metrics.cpu_percent == 25.0
        assert metrics.execution_time_seconds == 120.0
        assert metrics.memory_limit_mb == 500.0
    
    def test_is_within_memory_limit_true(self):
        """Test memory limit check when within limit."""
        metrics = PerformanceMetrics(
            memory_usage_mb=400.0,
            memory_percent=10.0,
            cpu_percent=25.0,
            execution_time_seconds=120.0,
            memory_limit_mb=500.0
        )
        
        assert metrics.is_within_memory_limit() is True
    
    def test_is_within_memory_limit_false(self):
        """Test memory limit check when exceeding limit."""
        metrics = PerformanceMetrics(
            memory_usage_mb=600.0,
            memory_percent=20.0,
            cpu_percent=25.0,
            execution_time_seconds=120.0,
            memory_limit_mb=500.0
        )
        
        assert metrics.is_within_memory_limit() is False
    
    def test_is_within_memory_limit_exact(self):
        """Test memory limit check when exactly at limit."""
        metrics = PerformanceMetrics(
            memory_usage_mb=500.0,
            memory_percent=15.0,
            cpu_percent=25.0,
            execution_time_seconds=120.0,
            memory_limit_mb=500.0
        )
        
        assert metrics.is_within_memory_limit() is True
    
    def test_get_memory_status_ok(self):
        """Test memory status string when within limit."""
        metrics = PerformanceMetrics(
            memory_usage_mb=300.0,
            memory_percent=10.0,
            cpu_percent=25.0,
            execution_time_seconds=120.0,
            memory_limit_mb=500.0
        )
        
        status = metrics.get_memory_status()
        assert "OK" in status
        assert "300.00 MB" in status
        assert "500.00 MB" in status
    
    def test_get_memory_status_exceeded(self):
        """Test memory status string when exceeding limit."""
        metrics = PerformanceMetrics(
            memory_usage_mb=600.0,
            memory_percent=20.0,
            cpu_percent=25.0,
            execution_time_seconds=120.0,
            memory_limit_mb=500.0
        )
        
        status = metrics.get_memory_status()
        assert "EXCEEDED" in status
        assert "600.00 MB" in status
        assert "500.00 MB" in status


class TestPerformanceMonitorInit:
    """Tests for PerformanceMonitor initialization."""
    
    def test_init_default_limit(self, mock_logger):
        """Test initialization with default memory limit."""
        with patch('src.performance_monitor.psutil.Process'):
            monitor = PerformanceMonitor(logger=mock_logger)
            
            assert monitor.memory_limit_mb == 500.0
            assert monitor.logger == mock_logger
    
    def test_init_custom_limit(self, mock_logger):
        """Test initialization with custom memory limit."""
        with patch('src.performance_monitor.psutil.Process'):
            monitor = PerformanceMonitor(memory_limit_mb=1000.0, logger=mock_logger)
            
            assert monitor.memory_limit_mb == 1000.0
    
    def test_init_creates_process(self, mock_logger):
        """Test that initialization creates psutil.Process."""
        with patch('src.performance_monitor.psutil.Process') as mock_process_class:
            with patch('src.performance_monitor.os.getpid', return_value=12345):
                monitor = PerformanceMonitor(logger=mock_logger)
                
                mock_process_class.assert_called_once_with(12345)


class TestGetCurrentMemoryUsage:
    """Tests for get_current_memory_usage method."""
    
    def test_get_memory_usage_success(self, performance_monitor, mock_process):
        """Test getting memory usage successfully."""
        # Mock returns 100 MB
        mock_process.memory_info.return_value = Mock(rss=100 * 1024 * 1024)
        
        memory_mb = performance_monitor.get_current_memory_usage()
        
        assert memory_mb == 100.0
    
    def test_get_memory_usage_different_values(self, performance_monitor, mock_process):
        """Test getting different memory usage values."""
        # Mock returns 250 MB
        mock_process.memory_info.return_value = Mock(rss=250 * 1024 * 1024)
        
        memory_mb = performance_monitor.get_current_memory_usage()
        
        assert memory_mb == 250.0
    
    def test_get_memory_usage_exception_handling(self, performance_monitor, mock_process):
        """Test exception handling when getting memory usage."""
        mock_process.memory_info.side_effect = Exception("Process error")
        
        memory_mb = performance_monitor.get_current_memory_usage()
        
        assert memory_mb == 0.0
        performance_monitor.logger.warning.assert_called_once()


class TestGetMemoryPercent:
    """Tests for get_memory_percent method."""
    
    def test_get_memory_percent_success(self, performance_monitor, mock_process):
        """Test getting memory percentage successfully."""
        mock_process.memory_percent.return_value = 15.5
        
        percent = performance_monitor.get_memory_percent()
        
        assert percent == 15.5
    
    def test_get_memory_percent_exception_handling(self, performance_monitor, mock_process):
        """Test exception handling when getting memory percentage."""
        mock_process.memory_percent.side_effect = Exception("Process error")
        
        percent = performance_monitor.get_memory_percent()
        
        assert percent == 0.0
        performance_monitor.logger.warning.assert_called_once()


class TestGetCpuPercent:
    """Tests for get_cpu_percent method."""
    
    def test_get_cpu_percent_success(self, performance_monitor, mock_process):
        """Test getting CPU percentage successfully."""
        mock_process.cpu_percent.return_value = 25.0
        
        cpu = performance_monitor.get_cpu_percent()
        
        assert cpu == 25.0
        mock_process.cpu_percent.assert_called_once_with(interval=0.1)
    
    def test_get_cpu_percent_custom_interval(self, performance_monitor, mock_process):
        """Test getting CPU percentage with custom interval."""
        mock_process.cpu_percent.return_value = 30.0
        
        cpu = performance_monitor.get_cpu_percent(interval=0.5)
        
        assert cpu == 30.0
        mock_process.cpu_percent.assert_called_once_with(interval=0.5)
    
    def test_get_cpu_percent_exception_handling(self, performance_monitor, mock_process):
        """Test exception handling when getting CPU percentage."""
        mock_process.cpu_percent.side_effect = Exception("Process error")
        
        cpu = performance_monitor.get_cpu_percent()
        
        assert cpu == 0.0
        performance_monitor.logger.warning.assert_called_once()


class TestCheckMemoryLimit:
    """Tests for check_memory_limit method."""
    
    def test_check_memory_limit_within(self, performance_monitor, mock_process):
        """Test memory limit check when within limit."""
        # Mock returns 300 MB (within 500 MB limit)
        mock_process.memory_info.return_value = Mock(rss=300 * 1024 * 1024)
        
        result = performance_monitor.check_memory_limit()
        
        assert result is True
        # Should not log warning
        performance_monitor.logger.warning.assert_not_called()
    
    def test_check_memory_limit_exceeded(self, performance_monitor, mock_process):
        """Test memory limit check when exceeding limit."""
        # Mock returns 600 MB (exceeds 500 MB limit)
        mock_process.memory_info.return_value = Mock(rss=600 * 1024 * 1024)
        
        result = performance_monitor.check_memory_limit()
        
        assert result is False
        # Should log warning
        performance_monitor.logger.warning.assert_called_once()
        assert "Memory limit exceeded" in performance_monitor.logger.warning.call_args[0][0]
    
    def test_check_memory_limit_exact(self, performance_monitor, mock_process):
        """Test memory limit check when exactly at limit."""
        # Mock returns exactly 500 MB
        mock_process.memory_info.return_value = Mock(rss=500 * 1024 * 1024)
        
        result = performance_monitor.check_memory_limit()
        
        assert result is True


class TestLogMemoryUsage:
    """Tests for log_memory_usage method."""
    
    def test_log_memory_usage_no_context(self, performance_monitor, mock_process):
        """Test logging memory usage without context."""
        mock_process.memory_info.return_value = Mock(rss=200 * 1024 * 1024)
        mock_process.memory_percent.return_value = 8.0
        
        performance_monitor.log_memory_usage()
        
        performance_monitor.logger.info.assert_called_once()
        log_message = performance_monitor.logger.info.call_args[0][0]
        assert "200.00 MB" in log_message
        assert "8.0%" in log_message
        assert "OK" in log_message
    
    def test_log_memory_usage_with_context(self, performance_monitor, mock_process):
        """Test logging memory usage with context."""
        mock_process.memory_info.return_value = Mock(rss=200 * 1024 * 1024)
        mock_process.memory_percent.return_value = 8.0
        
        performance_monitor.log_memory_usage(context="After scraping")
        
        performance_monitor.logger.info.assert_called_once()
        log_message = performance_monitor.logger.info.call_args[0][0]
        assert "[After scraping]" in log_message
    
    def test_log_memory_usage_exceeded(self, performance_monitor, mock_process):
        """Test logging memory usage when limit exceeded."""
        mock_process.memory_info.return_value = Mock(rss=600 * 1024 * 1024)
        mock_process.memory_percent.return_value = 20.0
        
        performance_monitor.log_memory_usage()
        
        performance_monitor.logger.info.assert_called_once()
        log_message = performance_monitor.logger.info.call_args[0][0]
        assert "600.00 MB" in log_message
        assert "EXCEEDED" in log_message


class TestGetMetrics:
    """Tests for get_metrics method."""
    
    def test_get_metrics_returns_complete_object(self, performance_monitor, mock_process):
        """Test that get_metrics returns complete PerformanceMetrics object."""
        mock_process.memory_info.return_value = Mock(rss=300 * 1024 * 1024)
        mock_process.memory_percent.return_value = 12.0
        mock_process.cpu_percent.return_value = 35.0
        
        metrics = performance_monitor.get_metrics(execution_time=120.5)
        
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.memory_usage_mb == 300.0
        assert metrics.memory_percent == 12.0
        assert metrics.cpu_percent == 35.0
        assert metrics.execution_time_seconds == 120.5
        assert metrics.memory_limit_mb == 500.0
    
    def test_get_metrics_default_execution_time(self, performance_monitor, mock_process):
        """Test get_metrics with default execution time."""
        mock_process.memory_info.return_value = Mock(rss=200 * 1024 * 1024)
        mock_process.memory_percent.return_value = 8.0
        mock_process.cpu_percent.return_value = 20.0
        
        metrics = performance_monitor.get_metrics()
        
        assert metrics.execution_time_seconds == 0.0


class TestLogMetrics:
    """Tests for log_metrics method."""
    
    def test_log_metrics_no_context(self, performance_monitor):
        """Test logging metrics without context."""
        metrics = PerformanceMetrics(
            memory_usage_mb=300.0,
            memory_percent=12.0,
            cpu_percent=35.0,
            execution_time_seconds=120.5,
            memory_limit_mb=500.0
        )
        
        performance_monitor.log_metrics(metrics)
        
        performance_monitor.logger.info.assert_called_once()
        log_message = performance_monitor.logger.info.call_args[0][0]
        assert "300.00 MB" in log_message
        assert "500.00 MB" in log_message
        assert "35.0%" in log_message
        assert "120.50s" in log_message
    
    def test_log_metrics_with_context(self, performance_monitor):
        """Test logging metrics with context."""
        metrics = PerformanceMetrics(
            memory_usage_mb=300.0,
            memory_percent=12.0,
            cpu_percent=35.0,
            execution_time_seconds=120.5,
            memory_limit_mb=500.0
        )
        
        performance_monitor.log_metrics(metrics, context="Final")
        
        performance_monitor.logger.info.assert_called_once()
        log_message = performance_monitor.logger.info.call_args[0][0]
        assert "[Final]" in log_message
    
    def test_log_metrics_exceeded_status(self, performance_monitor):
        """Test logging metrics when memory limit exceeded."""
        metrics = PerformanceMetrics(
            memory_usage_mb=600.0,
            memory_percent=20.0,
            cpu_percent=40.0,
            execution_time_seconds=180.0,
            memory_limit_mb=500.0
        )
        
        performance_monitor.log_metrics(metrics)
        
        performance_monitor.logger.info.assert_called_once()
        log_message = performance_monitor.logger.info.call_args[0][0]
        assert "EXCEEDED" in log_message
