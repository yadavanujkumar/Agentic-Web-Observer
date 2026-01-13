"""
Unit tests for benchmarking metrics
"""

import pytest
from src.benchmarking import MetricsTracker, CrawlMetrics, ResilienceMetrics
from pathlib import Path
import tempfile
import shutil


class TestMetricsTracker:
    """Test cases for MetricsTracker."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def tracker(self, temp_dir):
        """Create MetricsTracker instance."""
        return MetricsTracker(output_dir=temp_dir)
    
    def test_init(self, tracker):
        """Test tracker initialization."""
        assert isinstance(tracker.metrics_history, list)
        assert isinstance(tracker.resilience_history, list)
    
    def test_record_crawl(self, tracker):
        """Test recording a crawl."""
        metrics = tracker.record_crawl(
            crawler_type="vlm",
            goal="Test goal",
            start_url="https://example.com",
            success=True,
            pages_visited=5,
            data_extracted=[{"data": "test"}],
            duration=10.5,
            api_calls=3,
            total_tokens=1500
        )
        
        assert metrics.crawler_type == "vlm"
        assert metrics.success is True
        assert metrics.pages_visited == 5
        assert metrics.cost_usd > 0
    
    def test_calculate_success_rate(self, tracker):
        """Test success rate calculation."""
        # Record some successful and failed crawls
        tracker.record_crawl("vlm", "goal1", "url", True, 1, [], 1.0)
        tracker.record_crawl("vlm", "goal2", "url", True, 1, [], 1.0)
        tracker.record_crawl("vlm", "goal3", "url", False, 1, [], 1.0)
        
        success_rate = tracker.calculate_success_rate("vlm")
        assert success_rate == 2/3
    
    def test_record_resilience_test(self, tracker):
        """Test recording resilience test."""
        metrics = tracker.record_resilience_test(
            crawler_type="vlm",
            test_scenario="Class name changes",
            dom_changes=5,
            success_before=True,
            success_after=True
        )
        
        assert metrics.resilience_score == 1.0
        assert metrics.dom_changes_applied == 5


class TestCrawlMetrics:
    """Test cases for CrawlMetrics dataclass."""
    
    def test_creation(self):
        """Test creating CrawlMetrics."""
        metrics = CrawlMetrics(
            crawler_type="dom",
            goal="Extract data",
            start_url="https://example.com",
            success=True,
            pages_visited=3,
            data_points_extracted=10,
            duration_seconds=5.2,
            api_calls=0,
            total_tokens=0,
            cost_usd=0.0,
            errors=[],
            action_count=3,
            timestamp="2024-01-01T00:00:00"
        )
        
        assert metrics.crawler_type == "dom"
        assert metrics.success is True
        assert metrics.cost_usd == 0.0


if __name__ == "__main__":
    pytest.main([__file__])
