"""
Example: Run a benchmark duel between VLM and DOM crawlers
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.benchmarking import BenchmarkRunner
from src.utils import setup_directories, validate_api_keys


async def main():
    """Run a benchmark duel."""
    
    print("=" * 60)
    print("Agentic Web Observer - Benchmark Duel")
    print("=" * 60)
    
    # Setup
    setup_directories()
    
    # Validate API keys
    api_keys = validate_api_keys()
    if not api_keys["openai"]:
        print("\n⚠️  Warning: OpenAI API key not found!")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    # Configuration
    url = "https://books.toscrape.com/"
    goal = "Extract book titles and prices"
    
    # DOM selectors for the target site
    selectors = {
        "titles": "h3 a",
        "prices": ".price_color"
    }
    
    print(f"\n📍 Target URL: {url}")
    print(f"🎯 Goal: {goal}")
    print(f"\n⚔️  Starting duel...\n")
    
    # Initialize benchmark runner
    runner = BenchmarkRunner(
        vlm_provider="openai",
        vlm_model="gpt-4o",
        max_steps=10
    )
    
    try:
        # Run the duel
        results = await runner.run_duel(url, goal, selectors)
        
        # Results are automatically printed by the runner
        print("\n✅ Duel complete! Results saved to benchmarks/")
        
        # Display summary
        comparison = results['comparison']
        print(f"\n📊 Quick Summary:")
        print(f"   VLM: {'✅ Success' if comparison['vlm_success'] else '❌ Failed'} in {comparison['vlm_duration']:.2f}s (${comparison['vlm_cost']:.4f})")
        print(f"   DOM: {'✅ Success' if comparison['dom_success'] else '❌ Failed'} in {comparison['dom_duration']:.2f}s (${comparison['dom_cost']:.4f})")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
