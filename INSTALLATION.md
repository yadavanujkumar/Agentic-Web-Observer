# Installation Guide

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Git

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yadavanujkumar/Agentic-Web-Observer.git
cd Agentic-Web-Observer
```

### 2. Create Virtual Environment

**On Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

This will download the Chromium browser needed for automation.

### 5. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` file and add your API keys:

```env
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-google-api-key-here

# Choose your preferred provider
VLM_PROVIDER=openai
VLM_MODEL=gpt-4o
```

#### Getting API Keys:

**OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key and paste it in `.env`

**Google Gemini:**
1. Go to https://makersuite.google.com/app/apikey
2. Sign up or log in
3. Click "Create API Key"
4. Copy the key and paste it in `.env`

### 6. Verify Installation

```bash
python main.py validate
```

This command will check:
- API keys are configured
- Required directories exist
- Dependencies are installed

## Troubleshooting

### Playwright Installation Issues

If Playwright fails to install browsers:

```bash
# Install system dependencies (Linux)
playwright install-deps

# Then install browsers
playwright install chromium
```

### Permission Issues (Linux/Mac)

If you encounter permission errors:

```bash
chmod +x main.py
chmod +x examples/*.py
```

### Import Errors

If you get import errors, ensure you're in the project root and virtual environment is activated:

```bash
# Check current directory
pwd  # Should be in Agentic-Web-Observer/

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### API Key Issues

If API calls fail:

1. Verify keys are correctly set in `.env`
2. Check your API quota/credits
3. Ensure no extra spaces in the `.env` file
4. Try running: `python main.py validate`

## Next Steps

After successful installation:

1. Run a basic example: `python examples/basic_navigation.py`
2. Launch the dashboard: `python main.py dashboard`
3. Read the [Usage Guide](USAGE.md) for detailed usage instructions

## Docker Installation (Optional)

Coming soon: Docker support for easy deployment.

## System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Active internet connection for API calls
- **OS**: Windows 10+, macOS 10.14+, or Linux

## Optional Dependencies

### For Development

```bash
pip install pytest pytest-asyncio pytest-cov black flake8
```

### For Advanced Features

```bash
# Additional crawler support
pip install selenium webdriver-manager

# Advanced data processing
pip install jupyter notebook
```
