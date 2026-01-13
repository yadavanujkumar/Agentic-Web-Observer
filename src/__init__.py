"""Main package initialization."""

__version__ = "0.1.0"
__author__ = "Agentic Web Observer Team"

# Lazy imports to avoid dependency issues
__all__ = [
    'VisionEngine',
    'DetectedElement',
    'NavigationAgent',
    'NavigationState',
    'DOMCrawler',
    'SimpleSeleniumCrawler',
    'MetricsTracker',
    'BenchmarkRunner'
]


def __getattr__(name):
    """Lazy import of modules."""
    if name == 'VisionEngine' or name == 'DetectedElement':
        from .vision_engine import VisionEngine, DetectedElement
        return VisionEngine if name == 'VisionEngine' else DetectedElement
    elif name == 'NavigationAgent' or name == 'NavigationState':
        from .navigation import NavigationAgent, NavigationState
        return NavigationAgent if name == 'NavigationAgent' else NavigationState
    elif name == 'DOMCrawler' or name == 'SimpleSeleniumCrawler':
        from .crawler import DOMCrawler, SimpleSeleniumCrawler
        return DOMCrawler if name == 'DOMCrawler' else SimpleSeleniumCrawler
    elif name == 'MetricsTracker' or name == 'BenchmarkRunner':
        from .benchmarking import MetricsTracker, BenchmarkRunner
        return MetricsTracker if name == 'MetricsTracker' else BenchmarkRunner
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
