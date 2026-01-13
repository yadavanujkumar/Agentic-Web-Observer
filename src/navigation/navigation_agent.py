"""
Autonomous Navigation Agent using LangGraph for goal-based web navigation.
"""

import os
import asyncio
from typing import Dict, List, Optional, TypedDict, Annotated
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from ..vision_engine import VisionEngine, DetectedElement

load_dotenv()


class NavigationState(TypedDict):
    """State for the navigation agent."""
    goal: str
    current_url: str
    screenshot_path: str
    detected_elements: List[DetectedElement]
    action_history: List[Dict]
    step_count: int
    max_steps: int
    completed: bool
    error: Optional[str]
    reasoning: str


class NavigationAgent:
    """
    Autonomous navigation agent that uses VLM and LangGraph for web navigation.
    """
    
    def __init__(
        self,
        vision_provider: str = "openai",
        vision_model: str = "gpt-4o",
        llm_provider: str = "openai",
        max_steps: int = 20,
        headless: bool = False
    ):
        """
        Initialize the Navigation Agent.
        
        Args:
            vision_provider: VLM provider for vision analysis
            vision_model: Vision model to use
            llm_provider: LLM provider for reasoning
            max_steps: Maximum navigation steps
            headless: Whether to run browser in headless mode
        """
        self.vision_engine = VisionEngine(vision_provider, vision_model)
        self.max_steps = max_steps
        self.headless = headless
        
        # Setup LLM for reasoning
        if llm_provider == "openai":
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.2,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif llm_provider == "google":
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0.2,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
        
        # Build the LangGraph workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
        
        # Browser and page instances
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright_instance = None
        
        # Create screenshots directory
        self.screenshots_dir = Path("screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for navigation."""
        workflow = StateGraph(NavigationState)
        
        # Define nodes
        workflow.add_node("capture_screen", self.capture_screen_node)
        workflow.add_node("analyze_elements", self.analyze_elements_node)
        workflow.add_node("reason_action", self.reason_action_node)
        workflow.add_node("execute_action", self.execute_action_node)
        workflow.add_node("check_completion", self.check_completion_node)
        
        # Define edges
        workflow.set_entry_point("capture_screen")
        workflow.add_edge("capture_screen", "analyze_elements")
        workflow.add_edge("analyze_elements", "reason_action")
        workflow.add_edge("reason_action", "execute_action")
        workflow.add_edge("execute_action", "check_completion")
        
        # Conditional edge from check_completion
        workflow.add_conditional_edges(
            "check_completion",
            self.should_continue,
            {
                "continue": "capture_screen",
                "end": END
            }
        )
        
        return workflow
    
    async def initialize_browser(self, url: str):
        """Initialize Playwright browser."""
        self.playwright_instance = await async_playwright().start()
        self.browser = await self.playwright_instance.chromium.launch(headless=self.headless)
        context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = await context.new_page()
        await self.page.goto(url, wait_until="networkidle", timeout=30000)
    
    async def close_browser(self):
        """Close Playwright browser."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright_instance:
            await self.playwright_instance.stop()
    
    async def capture_screen_node(self, state: NavigationState) -> NavigationState:
        """Node to capture screenshot of current page."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = str(self.screenshots_dir / f"step_{state['step_count']}_{timestamp}.png")
            
            await self.page.screenshot(path=screenshot_path, full_page=False)
            
            state["screenshot_path"] = screenshot_path
            state["current_url"] = self.page.url
            
        except Exception as e:
            state["error"] = f"Screenshot capture error: {str(e)}"
        
        return state
    
    async def analyze_elements_node(self, state: NavigationState) -> NavigationState:
        """Node to analyze screenshot and detect elements."""
        try:
            context = f"Step {state['step_count']}/{state['max_steps']}"
            if state.get("action_history"):
                last_action = state["action_history"][-1]
                context += f" | Last action: {last_action.get('action_type', 'none')}"
            
            detected_elements = self.vision_engine.analyze_screenshot(
                state["screenshot_path"],
                state["goal"],
                context
            )
            
            state["detected_elements"] = detected_elements
            
        except Exception as e:
            state["error"] = f"Element analysis error: {str(e)}"
        
        return state
    
    async def reason_action_node(self, state: NavigationState) -> NavigationState:
        """Node to reason about next action using LLM."""
        try:
            elements_summary = "\n".join([
                f"- {elem.element_type}: {elem.description} "
                f"(confidence: {elem.confidence:.2f}, action: {elem.action})"
                for elem in state["detected_elements"][:5]  # Top 5 elements
            ])
            
            action_history_summary = "\n".join([
                f"Step {i+1}: {action.get('action_type', 'unknown')} on {action.get('description', 'unknown')}"
                for i, action in enumerate(state.get("action_history", [])[-3:])
            ])
            
            prompt = f"""You are a web navigation assistant working towards a goal.

Goal: {state['goal']}
Current URL: {state['current_url']}
Step: {state['step_count']}/{state['max_steps']}

Recent Actions:
{action_history_summary if action_history_summary else 'None yet'}

Detected Elements:
{elements_summary if elements_summary else 'No elements detected'}

Based on the goal and current state, decide:
1. Which element should we interact with next? (provide index 0-{len(state['detected_elements'])-1})
2. Is the goal achieved or unachievable?
3. Reasoning for your decision

Respond in this format:
ELEMENT_INDEX: <number or -1 if none suitable>
STATUS: continue/achieved/failed
REASONING: <your reasoning>
"""
            
            messages = [
                SystemMessage(content="You are an expert web navigation assistant."),
                HumanMessage(content=prompt)
            ]
            
            response = await asyncio.to_thread(self.llm.invoke, messages)
            reasoning = response.content
            
            state["reasoning"] = reasoning
            
        except Exception as e:
            state["error"] = f"Reasoning error: {str(e)}"
            state["reasoning"] = "Error in reasoning process"
        
        return state
    
    async def execute_action_node(self, state: NavigationState) -> NavigationState:
        """Node to execute the decided action."""
        try:
            reasoning = state.get("reasoning", "")
            
            # Parse reasoning to get element index and status
            element_index = -1
            status = "continue"
            
            for line in reasoning.split("\n"):
                if line.startswith("ELEMENT_INDEX:"):
                    try:
                        element_index = int(line.split(":")[1].strip())
                    except (ValueError, IndexError):
                        pass
                elif line.startswith("STATUS:"):
                    status = line.split(":")[1].strip().lower()
            
            # Check if we should stop
            if status in ["achieved", "failed"]:
                state["completed"] = True
                return state
            
            # Execute action if valid element index
            if 0 <= element_index < len(state["detected_elements"]):
                element = state["detected_elements"][element_index]
                
                # Calculate click coordinates
                click_x, click_y = self.vision_engine.calculate_click_coordinates(
                    element.bounding_box
                )
                
                # Perform action
                if element.action == "click":
                    await self.page.mouse.click(click_x, click_y)
                    await self.page.wait_for_timeout(2000)  # Wait for page to load
                
                elif element.action == "type":
                    # For input fields, click and type
                    await self.page.mouse.click(click_x, click_y)
                    await self.page.wait_for_timeout(500)
                    # Would need input text - for now just click
                
                elif element.action == "scroll":
                    await self.page.mouse.wheel(0, 500)
                    await self.page.wait_for_timeout(1000)
                
                # Record action
                action_record = {
                    "step": state["step_count"],
                    "action_type": element.action,
                    "description": element.description,
                    "element_type": element.element_type,
                    "coordinates": (click_x, click_y),
                    "reasoning": element.reasoning
                }
                
                if "action_history" not in state:
                    state["action_history"] = []
                state["action_history"].append(action_record)
            
            state["step_count"] += 1
            
        except Exception as e:
            state["error"] = f"Action execution error: {str(e)}"
        
        return state
    
    async def check_completion_node(self, state: NavigationState) -> NavigationState:
        """Node to check if navigation should continue."""
        # Check if max steps reached
        if state["step_count"] >= state["max_steps"]:
            state["completed"] = True
            if not state.get("error"):
                state["error"] = "Max steps reached"
        
        # Check if error occurred
        if state.get("error"):
            state["completed"] = True
        
        return state
    
    def should_continue(self, state: NavigationState) -> str:
        """Decide whether to continue navigation or end."""
        if state.get("completed", False):
            return "end"
        return "continue"
    
    async def navigate(self, url: str, goal: str) -> NavigationState:
        """
        Main navigation method.
        
        Args:
            url: Starting URL
            goal: Navigation goal
            
        Returns:
            Final navigation state
        """
        try:
            # Initialize browser
            await self.initialize_browser(url)
            
            # Initialize state
            initial_state: NavigationState = {
                "goal": goal,
                "current_url": url,
                "screenshot_path": "",
                "detected_elements": [],
                "action_history": [],
                "step_count": 0,
                "max_steps": self.max_steps,
                "completed": False,
                "error": None,
                "reasoning": ""
            }
            
            # Run the workflow
            final_state = None
            async for state in self.app.astream(initial_state):
                final_state = state
            
            return final_state
            
        except Exception as e:
            return {
                "goal": goal,
                "current_url": url,
                "error": f"Navigation error: {str(e)}",
                "completed": True,
                "step_count": 0,
                "action_history": []
            }
        
        finally:
            await self.close_browser()
