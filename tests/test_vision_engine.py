"""
Unit tests for Vision Engine
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.vision_engine import VisionEngine, DetectedElement


class TestVisionEngine:
    """Test cases for VisionEngine class."""
    
    def test_init_openai(self):
        """Test initialization with OpenAI provider."""
        with patch('src.vision_engine.vision_engine.OpenAI'):
            engine = VisionEngine(provider="openai", model="gpt-4o")
            assert engine.provider == "openai"
            assert engine.model == "gpt-4o"
    
    def test_init_google(self):
        """Test initialization with Google provider."""
        with patch('src.vision_engine.vision_engine.genai'):
            engine = VisionEngine(provider="google", model="gemini-1.5-pro")
            assert engine.provider == "google"
            assert engine.model == "gemini-1.5-pro"
    
    def test_init_invalid_provider(self):
        """Test initialization with invalid provider."""
        with pytest.raises(ValueError):
            VisionEngine(provider="invalid")
    
    def test_calculate_click_coordinates(self):
        """Test click coordinate calculation."""
        with patch('src.vision_engine.vision_engine.OpenAI'):
            engine = VisionEngine()
            
            # Test with bounding box (100, 200, 50, 30)
            x, y = engine.calculate_click_coordinates((100, 200, 50, 30))
            
            # Center should be at (125, 215)
            assert x == 125
            assert y == 215
    
    def test_build_analysis_prompt(self):
        """Test prompt building."""
        with patch('src.vision_engine.vision_engine.OpenAI'):
            engine = VisionEngine()
            
            prompt = engine._build_analysis_prompt(
                goal="Find login button",
                context="Homepage"
            )
            
            assert "Find login button" in prompt
            assert "Homepage" in prompt
            assert "JSON" in prompt
    
    def test_detected_element_creation(self):
        """Test DetectedElement dataclass."""
        element = DetectedElement(
            element_type="button",
            description="Login button",
            confidence=0.95,
            bounding_box=(100, 200, 50, 30),
            reasoning="Visible login text",
            action="click"
        )
        
        assert element.element_type == "button"
        assert element.confidence == 0.95
        assert element.action == "click"


class TestDetectedElement:
    """Test cases for DetectedElement dataclass."""
    
    def test_element_creation(self):
        """Test creating a detected element."""
        elem = DetectedElement(
            element_type="link",
            description="Contact page",
            confidence=0.8,
            bounding_box=(50, 60, 100, 20),
            reasoning="Link text visible",
            action="click"
        )
        
        assert elem.element_type == "link"
        assert elem.description == "Contact page"
        assert elem.bounding_box == (50, 60, 100, 20)


if __name__ == "__main__":
    pytest.main([__file__])
