"""Test configuration and fixtures."""

import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def sample_screenshot(test_data_dir):
    """Provide path to sample screenshot."""
    # In real tests, you'd have actual test images
    screenshot_path = test_data_dir / "sample_screenshot.png"
    return screenshot_path if screenshot_path.exists() else None


@pytest.fixture
def mock_env():
    """Mock environment variables."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ['OPENAI_API_KEY'] = 'test-openai-key'
    os.environ['GOOGLE_API_KEY'] = 'test-google-key'
    os.environ['VLM_PROVIDER'] = 'openai'
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_detected_elements():
    """Provide sample detected elements for testing."""
    from src.vision_engine import DetectedElement
    
    return [
        DetectedElement(
            element_type="button",
            description="Login button",
            confidence=0.95,
            bounding_box=(100, 200, 80, 40),
            reasoning="Contains 'Login' text",
            action="click"
        ),
        DetectedElement(
            element_type="input",
            description="Email input field",
            confidence=0.90,
            bounding_box=(100, 150, 200, 30),
            reasoning="Input field for email",
            action="type"
        )
    ]
