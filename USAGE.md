# Usage Guide

## Quick Start

### Command Line Interface

The main CLI provides several commands:

```bash
# Navigate with VLM
python main.py navigate --url <URL> --goal "<GOAL>"

# Run benchmark duel
python main.py duel --url <URL> --goal "<GOAL>"

# Launch dashboard
python main.py dashboard

# Validate setup
python main.py validate
```

## Detailed Usage

### 1. VLM Navigation

#### Basic Navigation

```bash
python main.py navigate \
  --url "https://books.toscrape.com/" \
  --goal "Find science fiction books"
```

#### Advanced Options

```bash
python main.py navigate \
  --url "https://example.com" \
  --goal "Find the cheapest laptop" \
  --provider openai \
  --model gpt-4o \
  --max-steps 30 \
  --headless
```

**Parameters:**
- `--url`: Target website URL (required)
- `--goal`: Navigation goal in natural language (required)
- `--provider`: VLM provider (openai/google, default: openai)
- `--model`: Model name (default: gpt-4o)
- `--max-steps`: Maximum navigation steps (default: 20)
- `--headless`: Run browser without GUI

### 2. Benchmark Duel

Compare VLM crawler against DOM-based crawler:

```bash
python main.py duel \
  --url "https://books.toscrape.com/" \
  --goal "Extract book titles and prices" \
  --selectors '{"titles": "h3 a", "prices": ".price_color"}'
```

**Parameters:**
- `--url`: Target website URL (required)
- `--goal`: Crawling goal (required)
- `--provider`: VLM provider (default: openai)
- `--selectors`: JSON string with CSS selectors for DOM crawler

### 3. Dashboard

Launch the interactive Streamlit dashboard:

```bash
python main.py dashboard
```

The dashboard will open at `http://localhost:8501` and provides:

- **Live Vision Feed**: Real-time element detection
- **Benchmark Duel**: Compare crawlers interactively
- **Metrics Dashboard**: View performance analytics
- **Configuration**: Manage API keys and settings

### 4. Python API

#### Basic Navigation

```python
import asyncio
from src.navigation import NavigationAgent

async def main():
    agent = NavigationAgent(
        vision_provider="openai",
        vision_model="gpt-4o",
        max_steps=20,
        headless=True
    )
    
    result = await agent.navigate(
        url="https://example.com",
        goal="Find contact information"
    )
    
    print(f"Steps: {result['step_count']}")
    print(f"Actions: {len(result['action_history'])}")

asyncio.run(main())
```

#### Vision Engine

```python
from src.vision_engine import VisionEngine

# Initialize engine
engine = VisionEngine(provider="openai", model="gpt-4o")

# Analyze screenshot
elements = engine.analyze_screenshot(
    screenshot_path="screenshot.png",
    goal="Find login form",
    context="Homepage of website"
)

# Process elements
for elem in elements:
    print(f"{elem.description}: {elem.confidence}")
    
    # Get click coordinates
    x, y = engine.calculate_click_coordinates(elem.bounding_box)
    print(f"Click at: ({x}, {y})")

# Visualize detections
engine.draw_bounding_boxes(
    screenshot_path="screenshot.png",
    elements=elements,
    output_path="annotated.png"
)
```

#### Benchmark Runner

```python
import asyncio
from src.benchmarking import BenchmarkRunner

async def run_benchmark():
    runner = BenchmarkRunner(
        vlm_provider="openai",
        vlm_model="gpt-4o",
        max_steps=20
    )
    
    # Run duel
    results = await runner.run_duel(
        url="https://example.com",
        goal="Extract product data",
        selectors={"products": ".product"}
    )
    
    # Access results
    print(f"Winner: {results['comparison']['winner']}")
    print(f"VLM Success: {results['comparison']['vlm_success']}")
    print(f"DOM Success: {results['comparison']['dom_success']}")

asyncio.run(run_benchmark())
```

#### Metrics Tracking

```python
from src.benchmarking import MetricsTracker

tracker = MetricsTracker()

# Record a crawl
tracker.record_crawl(
    crawler_type="vlm",
    goal="Find products",
    start_url="https://example.com",
    success=True,
    pages_visited=5,
    data_extracted=[...],
    duration=45.2,
    api_calls=10,
    total_tokens=15000
)

# Get metrics
success_rate = tracker.calculate_success_rate("vlm")
cost_metrics = tracker.calculate_cost_efficiency("vlm")
comparison = tracker.compare_crawlers()

# Export to CSV
tracker.export_to_csv("metrics.csv")
```

## Common Use Cases

### 1. E-commerce Scraping

```python
goal = "Find all laptops under $1000 and extract their names, prices, and ratings"
```

### 2. Form Automation

```python
goal = "Fill the contact form with name 'John Doe', email 'john@example.com', and submit"
```

### 3. Content Extraction

```python
goal = "Extract all article titles, authors, and publication dates from the news page"
```

### 4. Multi-step Navigation

```python
goal = "Navigate to the products page, filter by category 'Electronics', sort by price, and extract top 10 items"
```

## Tips & Best Practices

### 1. Writing Effective Goals

✅ **Good Goals:**
- "Find the login button and click it"
- "Extract all product prices from this page"
- "Navigate to the checkout page"

❌ **Vague Goals:**
- "Do something useful"
- "Find stuff"
- "Click things"

### 2. Optimizing Performance

- **Use headless mode** for production: `--headless`
- **Limit steps** for cost control: `--max-steps 10`
- **Choose appropriate models**: gpt-4o-mini for simpler tasks

### 3. Cost Management

- Monitor token usage in metrics dashboard
- Use DOM crawler when selectors are stable
- Set reasonable `max_steps` limits
- Cache screenshots when testing

### 4. Debugging

- **View screenshots**: Check `screenshots/` folder
- **Check action history**: Review `result['action_history']`
- **Use dashboard**: Live visualization helps debug
- **Enable verbose logging**: Check console output

## Advanced Features

### Custom Selectors for DOM Crawler

```python
selectors = {
    "titles": "h1.product-title",
    "prices": "span.price",
    "images": "img.product-image::attr(src)",
    "ratings": "div.rating::text"
}
```

### Resilience Testing

```python
from src.benchmarking import BenchmarkRunner

runner = BenchmarkRunner()

runner.run_resilience_test(
    url="https://example.com",
    goal="Extract data",
    dom_mutations=["class-name-change", "id-change"]
)
```

### Custom Vision Prompts

Extend the VisionEngine for specialized detection:

```python
from src.vision_engine import VisionEngine

class CustomVisionEngine(VisionEngine):
    def _build_analysis_prompt(self, goal, context):
        # Custom prompt engineering
        return f"Custom prompt for {goal}..."
```

## Troubleshooting

### Navigation Gets Stuck

- Increase `max_steps`
- Simplify the goal
- Check if site has anti-bot measures

### Poor Element Detection

- Ensure high-quality screenshots
- Provide better context
- Try different VLM models

### High Costs

- Use gpt-4o-mini instead of gpt-4o
- Reduce `max_steps`
- Cache results when possible

## Examples

See the `examples/` directory for:

- `basic_navigation.py`: Simple VLM navigation
- `benchmark_duel.py`: VLM vs DOM comparison
- `test_vision_engine.py`: Element detection testing

Run any example:

```bash
python examples/basic_navigation.py
```
