"""
Benchmarking and metrics tracking for VLM vs DOM-based crawlers.
"""

import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import pandas as pd


@dataclass
class CrawlMetrics:
    """Metrics for a single crawl session."""
    crawler_type: str  # 'vlm' or 'dom'
    goal: str
    start_url: str
    success: bool
    pages_visited: int
    data_points_extracted: int
    duration_seconds: float
    api_calls: int
    total_tokens: int
    cost_usd: float
    errors: List[str]
    action_count: int
    timestamp: str


@dataclass
class ResilienceMetrics:
    """Metrics for crawler resilience to code changes."""
    crawler_type: str
    test_scenario: str
    dom_changes_applied: int
    success_before: bool
    success_after: bool
    resilience_score: float  # 0.0 to 1.0
    failure_reason: Optional[str]


class MetricsTracker:
    """
    Track and calculate metrics for crawler performance.
    """
    
    def __init__(self, output_dir: str = "data"):
        """Initialize metrics tracker."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.metrics_file = self.output_dir / "metrics.json"
        self.metrics_history: List[CrawlMetrics] = []
        self.resilience_history: List[ResilienceMetrics] = []
        
        self._load_history()
    
    def _load_history(self):
        """Load existing metrics history."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.metrics_history = [
                        CrawlMetrics(**m) for m in data.get('crawl_metrics', [])
                    ]
                    self.resilience_history = [
                        ResilienceMetrics(**m) for m in data.get('resilience_metrics', [])
                    ]
            except Exception as e:
                print(f"Error loading metrics history: {e}")
    
    def _save_history(self):
        """Save metrics history to file."""
        data = {
            'crawl_metrics': [asdict(m) for m in self.metrics_history],
            'resilience_metrics': [asdict(m) for m in self.resilience_history]
        }
        
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_crawl(
        self,
        crawler_type: str,
        goal: str,
        start_url: str,
        success: bool,
        pages_visited: int,
        data_extracted: List,
        duration: float,
        api_calls: int = 0,
        total_tokens: int = 0,
        errors: List[str] = None
    ) -> CrawlMetrics:
        """
        Record metrics for a crawl session.
        
        Args:
            crawler_type: 'vlm' or 'dom'
            goal: Crawling goal
            start_url: Starting URL
            success: Whether crawl succeeded
            pages_visited: Number of pages visited
            data_extracted: Extracted data
            duration: Duration in seconds
            api_calls: Number of API calls (for VLM)
            total_tokens: Total tokens used (for VLM)
            errors: List of errors encountered
            
        Returns:
            CrawlMetrics object
        """
        # Calculate cost (rough estimates)
        cost = 0.0
        if crawler_type == 'vlm':
            # GPT-4o pricing: ~$0.01 per 1K tokens (combined input+output)
            cost = (total_tokens / 1000) * 0.01
        
        metrics = CrawlMetrics(
            crawler_type=crawler_type,
            goal=goal,
            start_url=start_url,
            success=success,
            pages_visited=pages_visited,
            data_points_extracted=len(data_extracted) if data_extracted else 0,
            duration_seconds=duration,
            api_calls=api_calls,
            total_tokens=total_tokens,
            cost_usd=cost,
            errors=errors or [],
            action_count=pages_visited,  # Simplified
            timestamp=datetime.now().isoformat()
        )
        
        self.metrics_history.append(metrics)
        self._save_history()
        
        return metrics
    
    def record_resilience_test(
        self,
        crawler_type: str,
        test_scenario: str,
        dom_changes: int,
        success_before: bool,
        success_after: bool,
        failure_reason: Optional[str] = None
    ) -> ResilienceMetrics:
        """
        Record resilience test results.
        
        Args:
            crawler_type: 'vlm' or 'dom'
            test_scenario: Description of test scenario
            dom_changes: Number of DOM changes applied
            success_before: Success before changes
            success_after: Success after changes
            failure_reason: Reason for failure if applicable
            
        Returns:
            ResilienceMetrics object
        """
        # Calculate resilience score
        if success_before and success_after:
            resilience_score = 1.0
        elif success_before and not success_after:
            resilience_score = 0.0
        elif not success_before:
            resilience_score = 0.5  # Baseline failure
        else:
            resilience_score = 0.5
        
        metrics = ResilienceMetrics(
            crawler_type=crawler_type,
            test_scenario=test_scenario,
            dom_changes_applied=dom_changes,
            success_before=success_before,
            success_after=success_after,
            resilience_score=resilience_score,
            failure_reason=failure_reason
        )
        
        self.resilience_history.append(metrics)
        self._save_history()
        
        return metrics
    
    def calculate_success_rate(self, crawler_type: Optional[str] = None) -> float:
        """
        Calculate success rate for a crawler type.
        
        Args:
            crawler_type: Filter by crawler type, or None for all
            
        Returns:
            Success rate (0.0 to 1.0)
        """
        metrics = self.metrics_history
        if crawler_type:
            metrics = [m for m in metrics if m.crawler_type == crawler_type]
        
        if not metrics:
            return 0.0
        
        successes = sum(1 for m in metrics if m.success)
        return successes / len(metrics)
    
    def calculate_avg_resilience(self, crawler_type: Optional[str] = None) -> float:
        """
        Calculate average resilience score.
        
        Args:
            crawler_type: Filter by crawler type, or None for all
            
        Returns:
            Average resilience score (0.0 to 1.0)
        """
        metrics = self.resilience_history
        if crawler_type:
            metrics = [m for m in metrics if m.crawler_type == crawler_type]
        
        if not metrics:
            return 0.0
        
        return sum(m.resilience_score for m in metrics) / len(metrics)
    
    def calculate_cost_efficiency(self, crawler_type: str = 'vlm') -> Dict:
        """
        Calculate cost efficiency metrics for VLM crawler.
        
        Args:
            crawler_type: Crawler type (default 'vlm')
            
        Returns:
            Dictionary with cost metrics
        """
        metrics = [m for m in self.metrics_history if m.crawler_type == crawler_type]
        
        if not metrics:
            return {
                "total_cost": 0.0,
                "avg_cost_per_crawl": 0.0,
                "cost_per_success": 0.0,
                "avg_tokens_per_crawl": 0
            }
        
        total_cost = sum(m.cost_usd for m in metrics)
        successful_metrics = [m for m in metrics if m.success]
        
        return {
            "total_cost": total_cost,
            "avg_cost_per_crawl": total_cost / len(metrics),
            "cost_per_success": total_cost / len(successful_metrics) if successful_metrics else 0.0,
            "avg_tokens_per_crawl": sum(m.total_tokens for m in metrics) / len(metrics)
        }
    
    def compare_crawlers(self) -> Dict:
        """
        Compare VLM and DOM-based crawlers.
        
        Returns:
            Comparison dictionary with metrics for both
        """
        vlm_metrics = [m for m in self.metrics_history if m.crawler_type == 'vlm']
        dom_metrics = [m for m in self.metrics_history if m.crawler_type == 'dom']
        
        comparison = {
            "vlm": {
                "count": len(vlm_metrics),
                "success_rate": self.calculate_success_rate('vlm'),
                "avg_duration": sum(m.duration_seconds for m in vlm_metrics) / len(vlm_metrics) if vlm_metrics else 0,
                "avg_resilience": self.calculate_avg_resilience('vlm'),
                "cost_metrics": self.calculate_cost_efficiency('vlm')
            },
            "dom": {
                "count": len(dom_metrics),
                "success_rate": self.calculate_success_rate('dom'),
                "avg_duration": sum(m.duration_seconds for m in dom_metrics) / len(dom_metrics) if dom_metrics else 0,
                "avg_resilience": self.calculate_avg_resilience('dom'),
                "cost_metrics": {"total_cost": 0.0, "note": "DOM crawler has no API costs"}
            }
        }
        
        return comparison
    
    def export_to_csv(self, filename: Optional[str] = None):
        """
        Export metrics to CSV for analysis.
        
        Args:
            filename: Output filename (optional)
        """
        if not filename:
            filename = self.output_dir / f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Convert metrics to DataFrame
        df = pd.DataFrame([asdict(m) for m in self.metrics_history])
        df.to_csv(filename, index=False)
        
        return filename
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics for all metrics."""
        return {
            "total_crawls": len(self.metrics_history),
            "total_resilience_tests": len(self.resilience_history),
            "overall_success_rate": self.calculate_success_rate(),
            "crawler_comparison": self.compare_crawlers(),
            "last_updated": datetime.now().isoformat()
        }
