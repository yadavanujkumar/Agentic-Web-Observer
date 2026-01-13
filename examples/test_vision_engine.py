"""
Example: Test vision engine element detection
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.vision_engine import VisionEngine
from src.utils import setup_directories, validate_api_keys


def main():
    """Test vision engine with a sample screenshot."""
    
    print("=" * 60)
    print("Agentic Web Observer - Vision Engine Test")
    print("=" * 60)
    
    # Setup
    setup_directories()
    
    # Validate API keys
    api_keys = validate_api_keys()
    if not api_keys["openai"]:
        print("\n⚠️  Warning: OpenAI API key not found!")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    # Check if there are any screenshots
    screenshots_dir = Path("screenshots")
    screenshots = list(screenshots_dir.glob("*.png"))
    
    if not screenshots:
        print("\n⚠️  No screenshots found in screenshots/")
        print("Please run a navigation example first to generate screenshots.")
        return
    
    # Use the most recent screenshot
    screenshot = sorted(screenshots)[-1]
    
    print(f"\n📸 Analyzing screenshot: {screenshot.name}")
    
    # Initialize vision engine
    vision_engine = VisionEngine(
        provider="openai",
        model="gpt-4o"
    )
    
    # Analyze screenshot
    goal = "Find interactive elements for shopping"
    
    print(f"🎯 Goal: {goal}")
    print("\n🔍 Detecting elements...\n")
    
    try:
        elements = vision_engine.analyze_screenshot(
            str(screenshot),
            goal
        )
        
        # Display results
        print(f"Found {len(elements)} elements:\n")
        
        for i, elem in enumerate(elements, 1):
            print(f"{i}. {elem.element_type.upper()}: {elem.description}")
            print(f"   Confidence: {elem.confidence:.2f}")
            print(f"   Action: {elem.action}")
            print(f"   Reasoning: {elem.reasoning}")
            print(f"   Bounding Box: {elem.bounding_box}")
            print()
        
        # Draw bounding boxes
        output_path = screenshots_dir / f"annotated_{screenshot.name}"
        vision_engine.draw_bounding_boxes(
            str(screenshot),
            elements,
            str(output_path)
        )
        
        print(f"✅ Annotated image saved to: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
