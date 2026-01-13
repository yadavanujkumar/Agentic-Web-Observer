# 🤖 Agentic Web Observer

An advanced **Agentic Multimodal Web Crawler** that uses Vision-Language Models (VLMs) for autonomous navigation and data extraction from complex, dynamic websites.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## 🌟 Features

### Visual Perception Engine
- **High-resolution screenshot capture** using Playwright
- **VLM-powered element detection** with GPT-4o-vision or Google Gemini
- **Intelligent identification** of interactive elements (buttons, forms, links, etc.)
- **Bounding box visualization** for detected elements

### Autonomous Navigation Loop
- **LangGraph-based agentic workflow** for goal-oriented navigation
- **AI reasoning** about next actions based on visual perception
- **Handles complex scenarios**: pop-ups, multi-step forms, infinite scroll
- **Adaptive behavior** without hardcoded selectors

### Benchmarking & Comparison
- **Duel Mode**: Compare VLM vs traditional DOM-based crawlers
- **Comprehensive metrics**: 
  - Success Rate
  - Resilience to DOM changes
  - Cost-to-Token Ratio
  - Performance metrics
- **Automated testing** against baseline crawlers

### Observability Dashboard
- **Streamlit-based UI** for real-time monitoring
- **Live Vision Feed** with bounding box highlighting
- **Action history** with reasoning explanations
- **Metrics visualization** with Plotly charts
- **Benchmark comparison views**

## 🏗️ Architecture

```
Agentic-Web-Observer/
├── src/
│   ├── vision_engine/       # VLM integration for element detection
│   ├── navigation/           # LangGraph-based navigation agent
│   ├── crawler/              # DOM-based crawlers for comparison
│   ├── benchmarking/         # Metrics tracking and benchmark runner
│   ├── dashboard/            # Streamlit observability dashboard
│   └── utils/                # Utility functions
├── examples/                 # Usage examples
├── tests/                    # Test suite
├── screenshots/              # Captured screenshots (auto-generated)
├── data/                     # Crawl data (auto-generated)
├── benchmarks/               # Benchmark results (auto-generated)
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yadavanujkumar/Agentic-Web-Observer.git
cd Agentic-Web-Observer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here
```

### 3. Run Examples

```bash
# Basic VLM navigation
python examples/basic_navigation.py

# Benchmark duel (VLM vs DOM)
python examples/benchmark_duel.py

# Test vision engine
python examples/test_vision_engine.py
```

### 4. Launch Dashboard

```bash
# Start Streamlit dashboard
streamlit run src/dashboard/streamlit_app.py
```

Access the dashboard at `http://localhost:8501`

## 📚 Usage

### Basic VLM Navigation

```python
import asyncio
from src.navigation import NavigationAgent

async def navigate():
    agent = NavigationAgent(
        vision_provider="openai",
        vision_model="gpt-4o",
        max_steps=20,
        headless=False
    )
    
    result = await agent.navigate(
        url="https://example.com",
        goal="Find the lowest priced laptop"
    )
    
    print(f"Steps: {result['step_count']}")
    print(f"Success: {result['completed']}")

asyncio.run(navigate())
```

### Vision Engine Element Detection

```python
from src.vision_engine import VisionEngine

engine = VisionEngine(provider="openai", model="gpt-4o")

elements = engine.analyze_screenshot(
    screenshot_path="screenshot.png",
    goal="Find login button",
    context="Homepage"
)

for elem in elements:
    print(f"{elem.element_type}: {elem.description}")
    print(f"Confidence: {elem.confidence}")
```

### Benchmark Duel

```python
import asyncio
from src.benchmarking import BenchmarkRunner

async def run_duel():
    runner = BenchmarkRunner(
        vlm_provider="openai",
        max_steps=20
    )
    
    results = await runner.run_duel(
        url="https://example.com",
        goal="Extract product prices",
        selectors={"prices": ".price"}
    )
    
    print(f"Winner: {results['comparison']['winner']}")

asyncio.run(run_duel())
```

## 🎯 Use Cases

1. **E-commerce Scraping**: Extract product information from dynamic websites
2. **Content Aggregation**: Collect articles, blogs, and news from various sources
3. **Form Automation**: Autonomously fill and submit multi-step forms
4. **Web Testing**: Test UI responsiveness and element accessibility
5. **Data Migration**: Extract data from legacy systems with complex UIs

## 🔧 Tech Stack

- **Core**: Python 3.12+
- **Browser Automation**: Playwright
- **AI/ML**: LangChain, LangGraph, OpenAI, Google Gemini
- **Traditional Crawling**: Scrapy, Selenium, BeautifulSoup
- **Data Processing**: Pandas, NumPy
- **Visualization**: Streamlit, Plotly, Matplotlib
- **Image Processing**: Pillow

## 📊 Performance Metrics

The system tracks:

- **Success Rate**: Percentage of goals achieved
- **Resilience Score**: Ability to handle DOM changes
- **Cost Efficiency**: Token usage and API costs
- **Speed**: Time to completion
- **Action Accuracy**: Precision of element identification

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o vision capabilities
- Google for Gemini vision models
- LangChain team for LangGraph framework
- Playwright team for browser automation tools

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for the future of web automation**