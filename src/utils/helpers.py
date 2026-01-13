"""Utility functions for the Agentic Web Observer."""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Configuration dictionary
    """
    load_dotenv()
    
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "google_api_key": os.getenv("GOOGLE_API_KEY"),
        "vlm_provider": os.getenv("VLM_PROVIDER", "openai"),
        "vlm_model": os.getenv("VLM_MODEL", "gpt-4o"),
        "max_navigation_steps": int(os.getenv("MAX_NAVIGATION_STEPS", "20")),
        "screenshot_quality": os.getenv("SCREENSHOT_QUALITY", "high"),
        "timeout_seconds": int(os.getenv("TIMEOUT_SECONDS", "30")),
        "streamlit_port": int(os.getenv("STREAMLIT_PORT", "8501")),
        "enable_live_feed": os.getenv("ENABLE_LIVE_FEED", "true").lower() == "true"
    }


def setup_directories():
    """Create necessary directories for the application."""
    directories = [
        "screenshots",
        "data",
        "benchmarks",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate that required API keys are set.
    
    Returns:
        Dictionary with validation results
    """
    config = load_config()
    
    return {
        "openai": bool(config["openai_api_key"]),
        "google": bool(config["google_api_key"])
    }


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
