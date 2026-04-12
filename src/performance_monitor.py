"""Performance monitoring utilities for tracking memory and execution time."""

import logging
import psutil
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Performance metrics for scraping operations."""
    
    memory_usage_mb: float
    memory_percent: float
    cpu_percent: float
    execution_time_seconds: float
    memory_limit_mb: float = 500.0
    
    def is_within_memory_limit(self) -> bool:
        """Check if memory usage is within the configured limit."""
        return self.memory_usage_mb <= self.memory_limit_mb
    
    def get_memory_status(self) -> str:
        """Get human-readable memory status."""
        status = "OK" if self.is_within_memory_limit() else "EXCEEDED"
        return f"{status} ({self.memory_usage_mb:.2f} MB / {self.memory_limit_mb:.2f} MB)"


class PerformanceMonitor:
    """Monitors memory usage and performance metrics during scraping."""
    
    def __init__(self, memory_limit_mb: float = 500.0, logger: Optional[logging.Logger] = None):
        """
        Initialize performance monitor.
        
        Args:
            memory_limit_mb: Memory limit in megabytes (default: 500 MB)
            logger: Logger instance for logging performance metrics
        """
        self.memory_limit_mb = memory_limit_mb
        self.logger = logger or logging.getLogger(__name__)
        self.process = psutil.Process(os.getpid())
        
        self.logger.debug(f"PerformanceMonitor initialized with memory limit: {memory_limit_mb} MB")
    
    def get_current_memory_usage(self) -> float:
        """
        Get current memory usage in megabytes.
        
        Returns:
            Memory usage in MB
        """
        try:
            # Get memory info for current process
            mem_info = self.process.memory_info()
            # RSS (Resident Set Size) is the actual physical memory used
            memory_mb = mem_info.rss / (1024 * 1024)
            return memory_mb
        except Exception as e:
            self.logger.warning(f"Error getting memory usage: {e}")
            return 0.0
    
    def get_memory_percent(self) -> float:
        """
        Get memory usage as percentage of total system memory.
        
        Returns:
            Memory usage percentage
        """
        try:
            return self.process.memory_percent()
        except Exception as e:
            self.logger.warning(f"Error getting memory percent: {e}")
            return 0.0
    
    def get_cpu_percent(self, interval: float = 0.1) -> float:
        """
        Get CPU usage percentage.
        
        Args:
            interval: Measurement interval in seconds
            
        Returns:
            CPU usage percentage
        """
        try:
            return self.process.cpu_percent(interval=interval)
        except Exception as e:
            self.logger.warning(f"Error getting CPU percent: {e}")
            return 0.0
    
    def check_memory_limit(self) -> bool:
        """
        Check if current memory usage is within the configured limit.
        
        Returns:
            True if within limit, False if exceeded
        """
        current_memory = self.get_current_memory_usage()
        within_limit = current_memory <= self.memory_limit_mb
        
        if not within_limit:
            self.logger.warning(
                f"Memory limit exceeded: {current_memory:.2f} MB / {self.memory_limit_mb:.2f} MB"
            )
        
        return within_limit
    
    def log_memory_usage(self, context: str = "") -> None:
        """
        Log current memory usage with optional context.
        
        Args:
            context: Optional context string to include in log message
        """
        memory_mb = self.get_current_memory_usage()
        memory_percent = self.get_memory_percent()
        
        context_str = f" [{context}]" if context else ""
        status = "OK" if memory_mb <= self.memory_limit_mb else "EXCEEDED"
        
        self.logger.info(
            f"Memory usage{context_str}: {memory_mb:.2f} MB "
            f"({memory_percent:.1f}% of system) - Status: {status}"
        )
    
    def get_metrics(self, execution_time: float = 0.0) -> PerformanceMetrics:
        """
        Get current performance metrics.
        
        Args:
            execution_time: Execution time in seconds
            
        Returns:
            PerformanceMetrics object with current metrics
        """
        return PerformanceMetrics(
            memory_usage_mb=self.get_current_memory_usage(),
            memory_percent=self.get_memory_percent(),
            cpu_percent=self.get_cpu_percent(),
            execution_time_seconds=execution_time,
            memory_limit_mb=self.memory_limit_mb
        )
    
    def log_metrics(self, metrics: PerformanceMetrics, context: str = "") -> None:
        """
        Log performance metrics.
        
        Args:
            metrics: PerformanceMetrics object to log
            context: Optional context string
        """
        context_str = f" [{context}]" if context else ""
        
        self.logger.info(
            f"Performance metrics{context_str}:\n"
            f"  Memory: {metrics.get_memory_status()}\n"
            f"  CPU: {metrics.cpu_percent:.1f}%\n"
            f"  Execution time: {metrics.execution_time_seconds:.2f}s"
        )
