"""Benchmarking module for comparing crawlers."""

from .metrics import MetricsTracker, CrawlMetrics, ResilienceMetrics

__all__ = [
    'MetricsTracker',
    'CrawlMetrics',
    'ResilienceMetrics',
    'BenchmarkRunner'
]


def __getattr__(name):
    """Lazy import of BenchmarkRunner."""
    if name == 'BenchmarkRunner':
        from .benchmark_runner import BenchmarkRunner
        return BenchmarkRunner
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
