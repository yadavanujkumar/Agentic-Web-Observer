"""
Unit tests for utility functions
"""

import pytest
from src.utils import (
    format_duration,
    truncate_text,
    setup_directories,
    validate_api_keys
)
from pathlib import Path
import os
from unittest.mock import patch


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_format_duration_seconds(self):
        """Test duration formatting for seconds."""
        assert format_duration(30.5) == "30.50s"
        assert format_duration(5.123) == "5.12s"
    
    def test_format_duration_minutes(self):
        """Test duration formatting for minutes."""
        result = format_duration(125.0)  # 2.08 minutes
        assert "m" in result
    
    def test_format_duration_hours(self):
        """Test duration formatting for hours."""
        result = format_duration(7200.0)  # 2 hours
        assert "h" in result
    
    def test_truncate_text_short(self):
        """Test truncating short text."""
        text = "Short text"
        result = truncate_text(text, max_length=50)
        assert result == text
    
    def test_truncate_text_long(self):
        """Test truncating long text."""
        text = "This is a very long text that should be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) <= 20
        assert result.endswith("...")
    
    def test_setup_directories(self, tmp_path):
        """Test directory setup."""
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            setup_directories()
            
            # Check that directories were created
            assert (tmp_path / "screenshots").exists()
            assert (tmp_path / "data").exists()
            assert (tmp_path / "benchmarks").exists()
            assert (tmp_path / "logs").exists()
        finally:
            os.chdir(original_dir)
    
    def test_validate_api_keys(self):
        """Test API key validation."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'GOOGLE_API_KEY': ''
        }):
            result = validate_api_keys()
            assert result['openai'] is True
            assert result['google'] is False


if __name__ == "__main__":
    pytest.main([__file__])
