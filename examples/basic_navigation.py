"""
Example: Basic VLM-based web navigation
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.navigation import NavigationAgent
from src.utils import setup_directories, validate_api_keys


async def main():
    """Run a basic VLM navigation example."""
    
    print("=" * 60)
    print("Agentic Web Observer - Basic Navigation Example")
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
    goal = "Find and identify science fiction books with their prices"
    
    print(f"\n📍 Target URL: {url}")
    print(f"🎯 Goal: {goal}")
    print(f"\n🚀 Starting navigation...\n")
    
    # Initialize agent
    agent = NavigationAgent(
        vision_provider="openai",
        vision_model="gpt-4o",
        max_steps=10,
        headless=False  # Set to True to hide browser
    )
    
    try:
        # Run navigation
        final_state = await agent.navigate(url, goal)
        
        # Display results
        print("\n" + "=" * 60)
        print("Navigation Complete!")
        print("=" * 60)
        
        print(f"\nSteps taken: {final_state.get('step_count', 0)}")
        print(f"Success: {final_state.get('completed', False)}")
        
        if final_state.get('error'):
            print(f"Error: {final_state.get('error')}")
        
        print(f"\nAction History:")
        for i, action in enumerate(final_state.get('action_history', [])[:5], 1):
            print(f"  {i}. {action.get('action_type', 'unknown').upper()}: {action.get('description', 'N/A')}")
        
        print(f"\n📸 Screenshots saved to: screenshots/")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
