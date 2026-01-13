"""Main package initialization."""

__version__ = "0.1.0"
__author__ = "Agentic Web Observer Team"

from .vision_engine import VisionEngine, DetectedElement
from .navigation import NavigationAgent, NavigationState
from .crawler import DOMCrawler, SimpleSeleniumCrawler
from .benchmarking import MetricsTracker, BenchmarkRunner

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
