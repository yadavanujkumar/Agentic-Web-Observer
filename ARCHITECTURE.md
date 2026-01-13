# Project Architecture

## Overview

The Agentic Web Observer is a sophisticated multimodal web crawler that combines Vision-Language Models with autonomous navigation capabilities.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  CLI (main.py) │  │ Streamlit UI   │  │  Examples    │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────┐
│                      Core Engine Layer                         │
│                                                                │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐   │
│  │ Vision Engine  │  │ Navigation     │  │ Benchmarking │   │
│  │ (VLM)          │  │ Agent          │  │ System       │   │
│  │                │  │ (LangGraph)    │  │              │   │
│  └────────────────┘  └────────────────┘  └──────────────┘   │
└────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────┐
│                   Browser Automation Layer                     │
│                                                                │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐   │
│  │  Playwright    │  │  Scrapy/       │  │  Screenshot  │   │
│  │  (async)       │  │  Selenium      │  │  Capture     │   │
│  └────────────────┘  └────────────────┘  └──────────────┘   │
└────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────┐
│                     External Services Layer                    │
│                                                                │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐   │
│  │ OpenAI API     │  │ Google Gemini  │  │  Target      │   │
│  │ (GPT-4o)       │  │ API            │  │  Websites    │   │
│  └────────────────┘  └────────────────┘  └──────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Vision Engine (`src/vision_engine/`)

**Purpose**: Visual element detection using VLMs

**Key Features**:
- Screenshot analysis with VLMs (GPT-4o, Gemini)
- Element detection (buttons, links, inputs, etc.)
- Bounding box extraction
- Confidence scoring
- Visual reasoning

**Main Classes**:
- `VisionEngine`: Main class for VLM integration
- `DetectedElement`: Data class for detected elements

**Dependencies**: OpenAI, Google Generative AI, Pillow

### 2. Navigation Agent (`src/navigation/`)

**Purpose**: Autonomous web navigation using LangGraph

**Key Features**:
- Goal-based navigation
- LangGraph workflow for decision making
- Playwright browser automation
- Pop-up and form handling
- Action history tracking

**Main Classes**:
- `NavigationAgent`: Main autonomous navigation class
- `NavigationState`: State management for navigation workflow

**Workflow**:
1. Capture screenshot
2. Analyze elements (VLM)
3. Reason about next action (LLM)
4. Execute action (Playwright)
5. Check completion
6. Loop or end

**Dependencies**: Playwright, LangGraph, LangChain, OpenAI

### 3. DOM-based Crawler (`src/crawler/`)

**Purpose**: Traditional web crawling for benchmarking

**Key Features**:
- Scrapy-based crawling
- Selenium support
- CSS selector-based extraction
- Baseline for comparison

**Main Classes**:
- `DOMCrawler`: Scrapy-based crawler
- `SimpleSeleniumCrawler`: Selenium-based alternative

**Dependencies**: Scrapy, Selenium, BeautifulSoup

### 4. Benchmarking System (`src/benchmarking/`)

**Purpose**: Performance tracking and comparison

**Key Features**:
- Metrics tracking (success rate, resilience, cost)
- Duel mode (VLM vs DOM)
- Cost-to-token analysis
- Resilience testing
- CSV export

**Main Classes**:
- `MetricsTracker`: Metrics collection and analysis
- `BenchmarkRunner`: Automated benchmarking
- `CrawlMetrics`: Crawl session metrics
- `ResilienceMetrics`: Resilience test metrics

**Dependencies**: Pandas

### 5. Observability Dashboard (`src/dashboard/`)

**Purpose**: Real-time monitoring and visualization

**Key Features**:
- Live vision feed
- Bounding box visualization
- Action history display
- Metrics charts
- Configuration UI

**Main Files**:
- `streamlit_app.py`: Main dashboard application

**Dependencies**: Streamlit, Plotly

## Data Flow

### VLM Navigation Flow

```
User Goal → Navigation Agent → Playwright (capture screenshot)
                    ↓
         Screenshot → Vision Engine → VLM API
                    ↓
         Detected Elements → LLM Reasoning
                    ↓
         Action Decision → Playwright Execution
                    ↓
         New Page State → Loop or Complete
```

### Benchmark Duel Flow

```
Benchmark Request → VLM Crawler (parallel) DOM Crawler
                          ↓                    ↓
                   VLM Results          DOM Results
                          ↓                    ↓
                          → Metrics Tracker ←
                                  ↓
                          Comparison Report
```

## Configuration

### Environment Variables (.env)

```env
OPENAI_API_KEY=sk-xxx
GOOGLE_API_KEY=xxx
VLM_PROVIDER=openai
VLM_MODEL=gpt-4o
MAX_NAVIGATION_STEPS=20
SCREENSHOT_QUALITY=high
TIMEOUT_SECONDS=30
```

### Directory Structure

```
├── screenshots/     # Captured screenshots
├── data/           # Crawl data and metrics
├── benchmarks/     # Benchmark results
└── logs/           # Application logs
```

## API Design

### Vision Engine API

```python
engine = VisionEngine(provider="openai", model="gpt-4o")
elements = engine.analyze_screenshot(
    screenshot_path="page.png",
    goal="Find login button",
    context="Homepage"
)
```

### Navigation Agent API

```python
agent = NavigationAgent(
    vision_provider="openai",
    max_steps=20,
    headless=True
)
result = await agent.navigate(
    url="https://example.com",
    goal="Find products"
)
```

### Benchmarking API

```python
runner = BenchmarkRunner(vlm_provider="openai")
results = await runner.run_duel(
    url="https://example.com",
    goal="Extract data",
    selectors={"data": ".selector"}
)
```

## Scalability Considerations

### Performance Optimization

1. **Caching**: Screenshot and VLM response caching
2. **Parallel Processing**: Multiple crawlers in parallel
3. **Async Operations**: Playwright async API
4. **Rate Limiting**: API call throttling

### Cost Optimization

1. **Model Selection**: gpt-4o-mini for simpler tasks
2. **Step Limits**: Maximum navigation steps
3. **Screenshot Quality**: Adjustable quality settings
4. **Batch Processing**: Group similar tasks

## Security Considerations

1. **API Keys**: Stored in .env, never committed
2. **Input Validation**: URL and goal validation
3. **Rate Limiting**: Prevent API abuse
4. **Sandbox Environment**: Isolated browser contexts

## Testing Strategy

### Unit Tests
- Vision engine element detection
- Metrics calculations
- Utility functions

### Integration Tests
- VLM API integration (mocked)
- Navigation workflows
- Benchmarking pipelines

### End-to-End Tests
- Full navigation scenarios
- Benchmark duels
- Dashboard functionality

## Future Enhancements

1. **Multi-page Navigation**: Session persistence across pages
2. **CAPTCHA Handling**: Visual CAPTCHA solving
3. **Form Intelligence**: Automatic form field detection
4. **Distributed Crawling**: Multi-worker architecture
5. **Custom VLM Fine-tuning**: Domain-specific models
6. **Advanced Analytics**: ML-based success prediction
7. **Docker Support**: Containerized deployment
8. **API Server**: REST API for programmatic access

## Performance Metrics

### Tracked Metrics

1. **Success Rate**: Goal achievement percentage
2. **Resilience Score**: Ability to handle DOM changes
3. **Cost Efficiency**: Tokens per successful crawl
4. **Speed**: Average time to completion
5. **Accuracy**: Element detection precision

### Benchmarking Results

Results stored in `benchmarks/` as JSON files with:
- Crawler comparison
- Success rates
- Duration metrics
- Cost analysis
- Winner determination
