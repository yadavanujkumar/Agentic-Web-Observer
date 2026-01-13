#!/usr/bin/env python
"""
Main CLI entry point for Agentic Web Observer.
"""

import asyncio
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.navigation import NavigationAgent
from src.benchmarking import BenchmarkRunner
from src.utils import setup_directories, validate_api_keys, load_config


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Agentic Web Observer - VLM-based Web Crawler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic navigation
  python main.py navigate --url https://example.com --goal "Find contact page"
  
  # Benchmark duel
  python main.py duel --url https://books.toscrape.com --goal "Extract book prices"
  
  # Launch dashboard
  python main.py dashboard
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Navigate command
    nav_parser = subparsers.add_parser("navigate", help="Run VLM navigation")
    nav_parser.add_argument("--url", required=True, help="Target URL")
    nav_parser.add_argument("--goal", required=True, help="Navigation goal")
    nav_parser.add_argument("--provider", default="openai", choices=["openai", "google"], help="VLM provider")
    nav_parser.add_argument("--model", default="gpt-4o", help="VLM model")
    nav_parser.add_argument("--max-steps", type=int, default=20, help="Maximum steps")
    nav_parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    
    # Duel command
    duel_parser = subparsers.add_parser("duel", help="Run benchmark duel")
    duel_parser.add_argument("--url", required=True, help="Target URL")
    duel_parser.add_argument("--goal", required=True, help="Crawling goal")
    duel_parser.add_argument("--provider", default="openai", choices=["openai", "google"], help="VLM provider")
    duel_parser.add_argument("--selectors", help="JSON string of CSS selectors for DOM crawler")
    
    # Dashboard command
    subparsers.add_parser("dashboard", help="Launch Streamlit dashboard")
    
    # Validate command
    subparsers.add_parser("validate", help="Validate API keys and setup")
    
    return parser.parse_args()


async def run_navigate(args):
    """Run navigation command."""
    print("\n🤖 Starting VLM Navigation...")
    print(f"URL: {args.url}")
    print(f"Goal: {args.goal}")
    print(f"Provider: {args.provider}")
    print()
    
    agent = NavigationAgent(
        vision_provider=args.provider,
        vision_model=args.model,
        max_steps=args.max_steps,
        headless=args.headless
    )
    
    result = await agent.navigate(args.url, args.goal)
    
    print("\n✅ Navigation Complete!")
    print(f"Steps: {result.get('step_count', 0)}")
    print(f"Success: {result.get('completed', False)}")
    
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    
    print(f"\n📸 Screenshots saved to: screenshots/")


async def run_duel(args):
    """Run benchmark duel command."""
    print("\n⚔️  Starting Benchmark Duel...")
    print(f"URL: {args.url}")
    print(f"Goal: {args.goal}")
    print()
    
    runner = BenchmarkRunner(
        vlm_provider=args.provider,
        max_steps=20
    )
    
    selectors = None
    if args.selectors:
        import json
        selectors = json.loads(args.selectors)
    
    results = await runner.run_duel(args.url, args.goal, selectors)
    
    print("\n📊 Results saved to: benchmarks/")


def run_dashboard(args):
    """Launch dashboard."""
    import subprocess
    
    print("\n🚀 Launching Streamlit Dashboard...")
    print("Dashboard will open at: http://localhost:8501")
    print("Press Ctrl+C to stop")
    print()
    
    dashboard_path = Path(__file__).parent / "src" / "dashboard" / "streamlit_app.py"
    subprocess.run(["streamlit", "run", str(dashboard_path)])


def run_validate(args):
    """Validate setup."""
    print("\n🔍 Validating Setup...\n")
    
    # Check API keys
    api_keys = validate_api_keys()
    
    print("API Keys:")
    print(f"  OpenAI: {'✅ Set' if api_keys['openai'] else '❌ Not set'}")
    print(f"  Google: {'✅ Set' if api_keys['google'] else '❌ Not set'}")
    
    # Check directories
    print("\nDirectories:")
    for dir_name in ["screenshots", "data", "benchmarks", "logs"]:
        dir_path = Path(dir_name)
        exists = dir_path.exists()
        print(f"  {dir_name}: {'✅ Exists' if exists else '❌ Missing'}")
    
    # Check dependencies
    print("\nKey Dependencies:")
    try:
        import playwright
        print("  Playwright: ✅ Installed")
    except ImportError:
        print("  Playwright: ❌ Not installed")
    
    try:
        import langchain
        print("  LangChain: ✅ Installed")
    except ImportError:
        print("  LangChain: ❌ Not installed")
    
    try:
        import streamlit
        print("  Streamlit: ✅ Installed")
    except ImportError:
        print("  Streamlit: ❌ Not installed")
    
    print("\n✅ Validation complete!")


def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup directories
    setup_directories()
    
    # Route to command
    if args.command == "navigate":
        asyncio.run(run_navigate(args))
    elif args.command == "duel":
        asyncio.run(run_duel(args))
    elif args.command == "dashboard":
        run_dashboard(args)
    elif args.command == "validate":
        run_validate(args)
    else:
        print("Please specify a command. Use --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
