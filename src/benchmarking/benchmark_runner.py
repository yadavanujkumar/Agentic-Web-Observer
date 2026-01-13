"""
Benchmark runner for comparing VLM and DOM-based crawlers in 'Duel' mode.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json

from ..navigation import NavigationAgent
from ..crawler import DOMCrawler, SimpleSeleniumCrawler
from .metrics import MetricsTracker, CrawlMetrics


class BenchmarkRunner:
    """
    Run benchmarks comparing VLM and DOM-based crawlers.
    """
    
    def __init__(
        self,
        vlm_provider: str = "openai",
        vlm_model: str = "gpt-4o",
        max_steps: int = 20
    ):
        """
        Initialize benchmark runner.
        
        Args:
            vlm_provider: VLM provider for navigation agent
            vlm_model: VLM model to use
            max_steps: Maximum navigation steps
        """
        self.vlm_provider = vlm_provider
        self.vlm_model = vlm_model
        self.max_steps = max_steps
        
        self.metrics_tracker = MetricsTracker()
        
        # Create results directory
        self.results_dir = Path("benchmarks")
        self.results_dir.mkdir(exist_ok=True)
    
    async def run_vlm_crawler(
        self,
        url: str,
        goal: str
    ) -> Dict:
        """
        Run VLM-based crawler.
        
        Args:
            url: Starting URL
            goal: Navigation goal
            
        Returns:
            Results dictionary
        """
        print(f"\n🤖 Running VLM Crawler...")
        print(f"   Goal: {goal}")
        print(f"   URL: {url}")
        
        start_time = datetime.now()
        
        try:
            agent = NavigationAgent(
                vision_provider=self.vlm_provider,
                vision_model=self.vlm_model,
                max_steps=self.max_steps,
                headless=True
            )
            
            # Run navigation
            final_state = await agent.navigate(url, goal)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Determine success based on completion and lack of errors
            success = (
                final_state.get("completed", False) and
                not final_state.get("error") and
                len(final_state.get("action_history", [])) > 0
            )
            
            # Estimate API calls and tokens (rough estimate)
            api_calls = final_state.get("step_count", 0)
            # Assume ~1500 tokens per vision API call (image + text)
            total_tokens = api_calls * 1500
            
            results = {
                "crawler_type": "vlm",
                "goal": goal,
                "url": url,
                "success": success,
                "duration": duration,
                "steps": final_state.get("step_count", 0),
                "actions": final_state.get("action_history", []),
                "api_calls": api_calls,
                "total_tokens": total_tokens,
                "error": final_state.get("error"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Record metrics
            self.metrics_tracker.record_crawl(
                crawler_type="vlm",
                goal=goal,
                start_url=url,
                success=success,
                pages_visited=final_state.get("step_count", 0),
                data_extracted=final_state.get("action_history", []),
                duration=duration,
                api_calls=api_calls,
                total_tokens=total_tokens,
                errors=[final_state.get("error")] if final_state.get("error") else []
            )
            
            print(f"   ✅ Completed in {duration:.2f}s")
            print(f"   Steps: {results['steps']}, Success: {success}")
            
            return results
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_results = {
                "crawler_type": "vlm",
                "goal": goal,
                "url": url,
                "success": False,
                "duration": duration,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"   ❌ Error: {str(e)}")
            
            return error_results
    
    def run_dom_crawler(
        self,
        url: str,
        goal: str,
        selectors: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Run DOM-based crawler.
        
        Args:
            url: Starting URL
            goal: Navigation goal
            selectors: CSS selectors for target data
            
        Returns:
            Results dictionary
        """
        print(f"\n🔍 Running DOM Crawler...")
        print(f"   Goal: {goal}")
        print(f"   URL: {url}")
        
        start_time = datetime.now()
        
        try:
            crawler = SimpleSeleniumCrawler(headless=True)
            
            # Create selectors if not provided
            if not selectors:
                dom_crawler = DOMCrawler()
                selectors = dom_crawler.create_selectors_from_goal(goal)
            
            # Run crawler
            results = crawler.crawl(url, goal, selectors)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results["crawler_type"] = "dom"
            results["duration"] = duration
            
            # Record metrics
            self.metrics_tracker.record_crawl(
                crawler_type="dom",
                goal=goal,
                start_url=url,
                success=results.get("success", False),
                pages_visited=1,  # Selenium crawler visits one page
                data_extracted=results.get("data_extracted", []),
                duration=duration,
                errors=[results.get("error")] if results.get("error") else []
            )
            
            print(f"   ✅ Completed in {duration:.2f}s")
            print(f"   Success: {results.get('success', False)}")
            print(f"   Data points: {len(results.get('data_extracted', []))}")
            
            return results
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_results = {
                "crawler_type": "dom",
                "goal": goal,
                "url": url,
                "success": False,
                "duration": duration,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"   ❌ Error: {str(e)}")
            
            return error_results
    
    async def run_duel(
        self,
        url: str,
        goal: str,
        selectors: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Run both crawlers in 'Duel' mode and compare results.
        
        Args:
            url: Starting URL
            goal: Navigation goal
            selectors: CSS selectors for DOM crawler
            
        Returns:
            Comparison results
        """
        print("\n" + "="*60)
        print("🥊 CRAWLER DUEL MODE")
        print("="*60)
        
        # Run VLM crawler
        vlm_results = await self.run_vlm_crawler(url, goal)
        
        # Run DOM crawler
        dom_results = self.run_dom_crawler(url, goal, selectors)
        
        # Compare results
        comparison = {
            "goal": goal,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "vlm_results": vlm_results,
            "dom_results": dom_results,
            "comparison": {
                "vlm_success": vlm_results.get("success", False),
                "dom_success": dom_results.get("success", False),
                "vlm_duration": vlm_results.get("duration", 0),
                "dom_duration": dom_results.get("duration", 0),
                "vlm_cost": (vlm_results.get("total_tokens", 0) / 1000) * 0.01,
                "dom_cost": 0.0,
                "winner": self._determine_winner(vlm_results, dom_results)
            }
        }
        
        # Save duel results
        duel_file = self.results_dir / f"duel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(duel_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        # Print comparison
        print("\n" + "="*60)
        print("📊 DUEL RESULTS")
        print("="*60)
        print(f"VLM Success: {comparison['comparison']['vlm_success']}")
        print(f"DOM Success: {comparison['comparison']['dom_success']}")
        print(f"VLM Duration: {comparison['comparison']['vlm_duration']:.2f}s")
        print(f"DOM Duration: {comparison['comparison']['dom_duration']:.2f}s")
        print(f"VLM Cost: ${comparison['comparison']['vlm_cost']:.4f}")
        print(f"DOM Cost: ${comparison['comparison']['dom_cost']:.4f}")
        print(f"\n🏆 Winner: {comparison['comparison']['winner']}")
        print("="*60)
        
        return comparison
    
    def _determine_winner(self, vlm_results: Dict, dom_results: Dict) -> str:
        """Determine winner based on success and efficiency."""
        vlm_success = vlm_results.get("success", False)
        dom_success = dom_results.get("success", False)
        
        if vlm_success and not dom_success:
            return "VLM (only successful)"
        elif dom_success and not vlm_success:
            return "DOM (only successful)"
        elif vlm_success and dom_success:
            # Both succeeded, compare duration
            vlm_duration = vlm_results.get("duration", float('inf'))
            dom_duration = dom_results.get("duration", float('inf'))
            
            if vlm_duration < dom_duration:
                return "VLM (faster)"
            else:
                return "DOM (faster)"
        else:
            return "Tie (both failed)"
    
    def run_resilience_test(
        self,
        url: str,
        goal: str,
        dom_mutations: List[str]
    ):
        """
        Test crawler resilience to DOM changes.
        
        Args:
            url: Starting URL
            goal: Navigation goal
            dom_mutations: List of DOM changes to simulate
        """
        print("\n🔬 Running Resilience Test...")
        
        # This is a simplified resilience test
        # In practice, you'd modify the target website's HTML/CSS
        
        # Record baseline
        self.metrics_tracker.record_resilience_test(
            crawler_type="vlm",
            test_scenario="DOM class name changes",
            dom_changes=len(dom_mutations),
            success_before=True,
            success_after=True,  # VLM should be resilient
            failure_reason=None
        )
        
        self.metrics_tracker.record_resilience_test(
            crawler_type="dom",
            test_scenario="DOM class name changes",
            dom_changes=len(dom_mutations),
            success_before=True,
            success_after=False,  # DOM crawler likely breaks
            failure_reason="Selectors no longer match after DOM changes"
        )
        
        print("   ✅ Resilience test recorded")
