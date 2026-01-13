"""
Visual Perception Engine for VLM-based web element detection.
Uses Playwright for screenshot capture and VLMs for element identification.
"""

import base64
import io
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageDraw
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DetectedElement:
    """Represents a detected interactive element on a webpage."""
    element_type: str  # e.g., 'button', 'link', 'input'
    description: str
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (x, y, width, height)
    reasoning: str
    action: str  # e.g., 'click', 'type', 'scroll'


class VisionEngine:
    """
    Visual Perception Engine that uses VLMs to identify interactive elements.
    """
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4o"):
        """
        Initialize the Vision Engine.
        
        Args:
            provider: VLM provider ('openai' or 'google')
            model: Model name to use
        """
        self.provider = provider.lower()
        self.model = model
        self._setup_client()
        
    def _setup_client(self):
        """Setup the appropriate VLM client based on provider."""
        if self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif self.provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.client = genai.GenerativeModel(self.model)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_screenshot(
        self,
        screenshot_path: str,
        goal: str,
        context: Optional[str] = None
    ) -> List[DetectedElement]:
        """
        Analyze a screenshot to detect interactive elements relevant to the goal.
        
        Args:
            screenshot_path: Path to the screenshot
            goal: The navigation goal (e.g., "Find the lowest priced laptop")
            context: Optional context about the current page state
            
        Returns:
            List of detected interactive elements
        """
        prompt = self._build_analysis_prompt(goal, context)
        
        if self.provider == "openai":
            return self._analyze_with_openai(screenshot_path, prompt)
        elif self.provider == "google":
            return self._analyze_with_google(screenshot_path, prompt)
    
    def _build_analysis_prompt(self, goal: str, context: Optional[str] = None) -> str:
        """Build the prompt for VLM analysis."""
        base_prompt = f"""You are a web navigation assistant analyzing a screenshot of a webpage.

Goal: {goal}

Task: Identify all interactive elements (buttons, links, inputs, dropdowns, etc.) that could help achieve this goal.

For each element, provide:
1. Element type (button, link, input, dropdown, etc.)
2. Brief description (visible text or purpose)
3. Confidence score (0.0-1.0)
4. Bounding box coordinates (x, y, width, height) in pixels
5. Reasoning for why this element is relevant
6. Recommended action (click, type, scroll, etc.)

"""
        
        if context:
            base_prompt += f"\nCurrent context: {context}\n"
        
        base_prompt += """
Respond in JSON format with an array of elements:
[
  {
    "element_type": "button",
    "description": "Login button",
    "confidence": 0.95,
    "bounding_box": [100, 200, 80, 40],
    "reasoning": "This button likely leads to authentication",
    "action": "click"
  }
]

Focus on elements most relevant to the goal. Identify pop-ups, cookie banners, or obstacles if present.
"""
        return base_prompt
    
    def _analyze_with_openai(
        self,
        screenshot_path: str,
        prompt: str
    ) -> List[DetectedElement]:
        """Analyze screenshot using OpenAI's vision model."""
        import json
        
        base64_image = self.encode_image(screenshot_path)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from response
            elements_data = self._extract_json(content)
            
            return [
                DetectedElement(
                    element_type=elem.get("element_type", "unknown"),
                    description=elem.get("description", ""),
                    confidence=elem.get("confidence", 0.5),
                    bounding_box=tuple(elem.get("bounding_box", [0, 0, 0, 0])),
                    reasoning=elem.get("reasoning", ""),
                    action=elem.get("action", "click")
                )
                for elem in elements_data
            ]
            
        except Exception as e:
            print(f"Error analyzing with OpenAI: {e}")
            return []
    
    def _analyze_with_google(
        self,
        screenshot_path: str,
        prompt: str
    ) -> List[DetectedElement]:
        """Analyze screenshot using Google's Gemini vision model."""
        import json
        from PIL import Image
        
        try:
            image = Image.open(screenshot_path)
            
            response = self.client.generate_content([prompt, image])
            content = response.text
            
            # Extract JSON from response
            elements_data = self._extract_json(content)
            
            return [
                DetectedElement(
                    element_type=elem.get("element_type", "unknown"),
                    description=elem.get("description", ""),
                    confidence=elem.get("confidence", 0.5),
                    bounding_box=tuple(elem.get("bounding_box", [0, 0, 0, 0])),
                    reasoning=elem.get("reasoning", ""),
                    action=elem.get("action", "click")
                )
                for elem in elements_data
            ]
            
        except Exception as e:
            print(f"Error analyzing with Google: {e}")
            return []
    
    def _extract_json(self, content: str) -> List[Dict]:
        """Extract JSON array from response content."""
        import json
        import re
        
        # Try to find JSON array in the response
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Try to parse the entire content as JSON
        try:
            result = json.loads(content)
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and 'elements' in result:
                return result['elements']
        except json.JSONDecodeError:
            pass
        
        return []
    
    def draw_bounding_boxes(
        self,
        screenshot_path: str,
        elements: List[DetectedElement],
        output_path: str
    ) -> str:
        """
        Draw bounding boxes on screenshot for visualization.
        
        Args:
            screenshot_path: Path to original screenshot
            elements: List of detected elements
            output_path: Path to save annotated image
            
        Returns:
            Path to the annotated image
        """
        image = Image.open(screenshot_path)
        draw = ImageDraw.Draw(image)
        
        for i, elem in enumerate(elements):
            x, y, w, h = elem.bounding_box
            
            # Draw rectangle
            draw.rectangle(
                [x, y, x + w, y + h],
                outline="red" if elem.confidence > 0.7 else "yellow",
                width=3
            )
            
            # Draw label
            label = f"{elem.element_type}: {elem.description[:20]}"
            draw.text((x, y - 20), label, fill="red")
        
        image.save(output_path)
        return output_path
    
    def calculate_click_coordinates(
        self,
        bounding_box: Tuple[int, int, int, int]
    ) -> Tuple[int, int]:
        """
        Calculate the center coordinates for clicking an element.
        
        Args:
            bounding_box: (x, y, width, height)
            
        Returns:
            (x, y) coordinates for clicking
        """
        x, y, w, h = bounding_box
        return (x + w // 2, y + h // 2)
