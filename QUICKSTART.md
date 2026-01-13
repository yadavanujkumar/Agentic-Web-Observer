# 🚀 Quick Start Guide

Get up and running with the Agentic Web Observer in 5 minutes!

## Prerequisites

- Python 3.12+
- pip
- Git

## Installation (2 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/yadavanujkumar/Agentic-Web-Observer.git
cd Agentic-Web-Observer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Configure API keys
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY or GOOGLE_API_KEY
```

## Usage (3 minutes)

### 1. Run a Simple Navigation

```bash
python examples/basic_navigation.py
```

This will:
- Navigate to a test website
- Use VLM to detect elements
- Take screenshots (saved to `screenshots/`)
- Show action history

### 2. Launch the Dashboard

```bash
python main.py dashboard
```

Then open http://localhost:8501 in your browser to:
- Configure crawlers
- Run benchmark duels
- View metrics and charts
- See live vision feeds

### 3. Run a Benchmark Duel

```bash
python main.py duel \
  --url "https://books.toscrape.com/" \
  --goal "Extract book prices"
```

This compares VLM crawler vs DOM crawler and shows which performs better.

## CLI Commands

```bash
# Navigate to a website
python main.py navigate --url <URL> --goal "<GOAL>"

# Run benchmark duel
python main.py duel --url <URL> --goal "<GOAL>"

# Launch dashboard
python main.py dashboard

# Validate setup
python main.py validate

# Get help
python main.py --help
```

## Example Goals

Try these navigation goals:

- "Find the login button and click it"
- "Extract all product prices"
- "Navigate to the contact page"
- "Find the cheapest laptop"
- "Click on the science fiction category"

## Python API

```python
import asyncio
from src.navigation import NavigationAgent

async def main():
    agent = NavigationAgent(
        vision_provider="openai",
        max_steps=10,
        headless=False
    )
    
    result = await agent.navigate(
        url="https://example.com",
        goal="Find contact information"
    )
    
    print(f"Success: {result['completed']}")
    print(f"Steps: {result['step_count']}")

asyncio.run(main())
```

## Next Steps

- Read [INSTALLATION.md](INSTALLATION.md) for detailed setup
- Check [USAGE.md](USAGE.md) for comprehensive API docs
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for project overview

## Troubleshooting

### No API key error
- Make sure you've added your API key to `.env`
- Check that `.env` is in the project root

### Playwright error
- Run: `playwright install chromium`
- On Linux: `playwright install-deps`

### Import errors
- Activate virtual environment: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

## Getting Help

1. Check the documentation files
2. Run `python main.py validate`
3. Open a GitHub issue
4. Review example scripts in `examples/`

## What's Included?

✅ VLM-based element detection (GPT-4o, Gemini)  
✅ Autonomous navigation with LangGraph  
✅ Traditional DOM crawler for comparison  
✅ Comprehensive benchmarking system  
✅ Interactive Streamlit dashboard  
✅ CLI and Python API  
✅ Example scripts and tests  
✅ Full documentation  

---

**Ready to explore autonomous web crawling with AI? Let's go! 🚀**
