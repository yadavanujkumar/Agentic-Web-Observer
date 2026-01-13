"""
Streamlit Dashboard for Agentic Web Observer - Live Vision Feed & Metrics
"""

import streamlit as st
import json
import asyncio
from pathlib import Path
from datetime import datetime
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.navigation import NavigationAgent
from src.benchmarking import MetricsTracker, BenchmarkRunner
from src.vision_engine import VisionEngine


# Page config
st.set_page_config(
    page_title="Agentic Web Observer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success {
        color: #28a745;
    }
    .failure {
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'metrics_tracker' not in st.session_state:
        st.session_state.metrics_tracker = MetricsTracker()
    if 'current_crawl' not in st.session_state:
        st.session_state.current_crawl = None
    if 'live_feed_active' not in st.session_state:
        st.session_state.live_feed_active = False


def render_header():
    """Render the dashboard header."""
    st.markdown('<p class="main-header">🤖 Agentic Web Observer</p>', unsafe_allow_html=True)
    st.markdown("**Vision-Language Model-based Web Crawler with Live Observability**")
    st.markdown("---")


def render_sidebar():
    """Render the sidebar with controls."""
    st.sidebar.title("🎮 Control Panel")
    
    # Mode selection
    mode = st.sidebar.selectbox(
        "Select Mode",
        ["Live Vision Feed", "Benchmark Duel", "Metrics Dashboard", "Configure"]
    )
    
    st.sidebar.markdown("---")
    
    return mode


def render_live_vision_feed():
    """Render live vision feed mode."""
    st.header("🎥 Live Vision Feed")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Configuration")
        
        url = st.text_input("Target URL", value="https://example.com", key="live_url")
        goal = st.text_area(
            "Navigation Goal",
            value="Find the lowest priced laptop on this site",
            height=100,
            key="live_goal"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            vlm_provider = st.selectbox("VLM Provider", ["openai", "google"], key="live_vlm")
        with col_b:
            max_steps = st.slider("Max Steps", 5, 30, 20, key="live_steps")
        
        start_crawl = st.button("🚀 Start Crawl", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("Status")
        status_placeholder = st.empty()
        
        if st.session_state.live_feed_active:
            status_placeholder.success("🟢 Crawl in progress...")
        else:
            status_placeholder.info("⚪ Ready to start")
    
    # Vision feed display area
    st.markdown("---")
    st.subheader("Vision Feed & Element Detection")
    
    vision_col1, vision_col2 = st.columns([3, 2])
    
    with vision_col1:
        screenshot_placeholder = st.empty()
    
    with vision_col2:
        elements_placeholder = st.empty()
        reasoning_placeholder = st.empty()
    
    # Action history
    st.markdown("---")
    st.subheader("Action History")
    action_history_placeholder = st.empty()
    
    if start_crawl and not st.session_state.live_feed_active:
        st.session_state.live_feed_active = True
        
        with st.spinner("Initializing crawler..."):
            try:
                # Run the crawler
                async def run_crawler():
                    agent = NavigationAgent(
                        vision_provider=vlm_provider,
                        max_steps=max_steps,
                        headless=False
                    )
                    return await agent.navigate(url, goal)
                
                # Note: In a real implementation, this would need proper async handling
                # For Streamlit, we'd need to use threading or async execution
                st.warning("⚠️ Live feed requires async execution. Check screenshots folder for results.")
                
                # Show simulated live feed
                screenshots_dir = Path("screenshots")
                if screenshots_dir.exists():
                    screenshots = sorted(screenshots_dir.glob("*.png"))
                    
                    if screenshots:
                        for screenshot in screenshots[-5:]:  # Show last 5
                            img = Image.open(screenshot)
                            screenshot_placeholder.image(img, caption=screenshot.name, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                st.session_state.live_feed_active = False


def render_benchmark_duel():
    """Render benchmark duel mode."""
    st.header("🥊 Crawler Duel: VLM vs DOM")
    
    st.markdown("""
    Compare the VLM-based crawler against traditional DOM-based approaches.
    Track success rates, resilience, and cost-efficiency.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Test Configuration")
        
        url = st.text_input("Target URL", value="https://books.toscrape.com/", key="duel_url")
        goal = st.text_area(
            "Crawling Goal",
            value="Extract book titles and prices",
            height=100,
            key="duel_goal"
        )
        
        vlm_provider = st.selectbox("VLM Provider", ["openai", "google"], key="duel_vlm")
        
        # DOM selectors
        st.markdown("**DOM Crawler Selectors**")
        selector_key = st.text_input("Field Name", value="titles", key="selector_key")
        selector_value = st.text_input("CSS Selector", value="h3 a", key="selector_value")
    
    with col2:
        st.subheader("Quick Stats")
        
        metrics = st.session_state.metrics_tracker
        comparison = metrics.compare_crawlers()
        
        st.metric("VLM Success Rate", f"{comparison['vlm']['success_rate']:.1%}")
        st.metric("DOM Success Rate", f"{comparison['dom']['success_rate']:.1%}")
        st.metric("Total Duels", comparison['vlm']['count'] + comparison['dom']['count'])
    
    if st.button("⚔️ Start Duel", type="primary", use_container_width=True):
        with st.spinner("Running duel..."):
            try:
                runner = BenchmarkRunner(
                    vlm_provider=vlm_provider,
                    max_steps=20
                )
                
                selectors = {selector_key: selector_value} if selector_key else None
                
                # Note: This requires async execution
                st.warning("⚠️ Duel requires async execution. Check benchmarks folder for results.")
                
                # Show last duel result if available
                benchmarks_dir = Path("benchmarks")
                if benchmarks_dir.exists():
                    duel_files = sorted(benchmarks_dir.glob("duel_*.json"))
                    if duel_files:
                        with open(duel_files[-1], 'r') as f:
                            last_duel = json.load(f)
                        
                        st.markdown("---")
                        st.subheader("Latest Duel Results")
                        
                        result_col1, result_col2 = st.columns(2)
                        
                        with result_col1:
                            st.markdown("### 🤖 VLM Crawler")
                            vlm = last_duel['vlm_results']
                            st.write(f"✅ Success: {vlm.get('success', False)}")
                            st.write(f"⏱️ Duration: {vlm.get('duration', 0):.2f}s")
                            st.write(f"📊 Steps: {vlm.get('steps', 0)}")
                        
                        with result_col2:
                            st.markdown("### 🔍 DOM Crawler")
                            dom = last_duel['dom_results']
                            st.write(f"✅ Success: {dom.get('success', False)}")
                            st.write(f"⏱️ Duration: {dom.get('duration', 0):.2f}s")
                            st.write(f"📊 Data Points: {len(dom.get('data_extracted', []))}")
                        
                        st.markdown(f"### 🏆 Winner: {last_duel['comparison']['winner']}")
                
            except Exception as e:
                st.error(f"Error running duel: {str(e)}")


def render_metrics_dashboard():
    """Render metrics and analytics dashboard."""
    st.header("📊 Metrics Dashboard")
    
    metrics = st.session_state.metrics_tracker
    
    # Summary stats
    st.subheader("Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    summary = metrics.get_summary_stats()
    
    with col1:
        st.metric("Total Crawls", summary['total_crawls'])
    with col2:
        st.metric("Success Rate", f"{summary['overall_success_rate']:.1%}")
    with col3:
        st.metric("Resilience Tests", summary['total_resilience_tests'])
    with col4:
        comparison = summary['crawler_comparison']
        vlm_avg_dur = comparison['vlm']['avg_duration']
        st.metric("Avg Duration (VLM)", f"{vlm_avg_dur:.2f}s")
    
    st.markdown("---")
    
    # Comparison charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Success Rate Comparison")
        
        comparison = metrics.compare_crawlers()
        
        fig = go.Figure(data=[
            go.Bar(
                name='Success Rate',
                x=['VLM', 'DOM'],
                y=[
                    comparison['vlm']['success_rate'] * 100,
                    comparison['dom']['success_rate'] * 100
                ],
                marker_color=['#667eea', '#764ba2']
            )
        ])
        
        fig.update_layout(
            yaxis_title="Success Rate (%)",
            yaxis_range=[0, 100],
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Resilience Score Comparison")
        
        fig = go.Figure(data=[
            go.Bar(
                name='Resilience',
                x=['VLM', 'DOM'],
                y=[
                    comparison['vlm']['avg_resilience'] * 100,
                    comparison['dom']['avg_resilience'] * 100
                ],
                marker_color=['#28a745', '#ffc107']
            )
        ])
        
        fig.update_layout(
            yaxis_title="Resilience Score (%)",
            yaxis_range=[0, 100],
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Cost analysis
    st.markdown("---")
    st.subheader("Cost Analysis (VLM)")
    
    cost_metrics = metrics.calculate_cost_efficiency('vlm')
    
    cost_col1, cost_col2, cost_col3 = st.columns(3)
    
    with cost_col1:
        st.metric("Total Cost", f"${cost_metrics['total_cost']:.4f}")
    with cost_col2:
        st.metric("Avg Cost/Crawl", f"${cost_metrics['avg_cost_per_crawl']:.4f}")
    with cost_col3:
        st.metric("Cost/Success", f"${cost_metrics['cost_per_success']:.4f}")
    
    # Crawl history
    st.markdown("---")
    st.subheader("Recent Crawls")
    
    if metrics.metrics_history:
        recent_crawls = metrics.metrics_history[-10:]  # Last 10
        
        df = pd.DataFrame([
            {
                "Type": m.crawler_type.upper(),
                "Goal": m.goal[:40] + "..." if len(m.goal) > 40 else m.goal,
                "Success": "✅" if m.success else "❌",
                "Duration": f"{m.duration_seconds:.2f}s",
                "Pages": m.pages_visited,
                "Cost": f"${m.cost_usd:.4f}",
                "Time": datetime.fromisoformat(m.timestamp).strftime("%Y-%m-%d %H:%M")
            }
            for m in reversed(recent_crawls)
        ])
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No crawl history yet. Run some crawls to see metrics!")


def render_configure():
    """Render configuration page."""
    st.header("⚙️ Configuration")
    
    st.subheader("API Keys")
    st.markdown("Configure your API keys for VLM providers.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        openai_key = st.text_input("OpenAI API Key", type="password", key="openai_key")
        if st.button("Save OpenAI Key"):
            st.success("✅ OpenAI key saved (demo)")
    
    with col2:
        google_key = st.text_input("Google API Key", type="password", key="google_key")
        if st.button("Save Google Key"):
            st.success("✅ Google key saved (demo)")
    
    st.markdown("---")
    st.subheader("Crawler Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_provider = st.selectbox("Default VLM Provider", ["openai", "google"])
        default_model = st.selectbox("Default Model", ["gpt-4o", "gpt-4-turbo", "gemini-1.5-pro-vision"])
    
    with col2:
        default_max_steps = st.slider("Default Max Steps", 5, 50, 20)
        screenshot_quality = st.selectbox("Screenshot Quality", ["low", "medium", "high"])
    
    if st.button("💾 Save Configuration", type="primary"):
        st.success("✅ Configuration saved!")
    
    st.markdown("---")
    st.subheader("About")
    
    st.markdown("""
    **Agentic Web Observer** is a multimodal web crawler that uses Vision-Language Models
    for autonomous navigation and data extraction from complex, dynamic websites.
    
    **Features:**
    - 🔍 Visual element detection using VLMs
    - 🤖 Autonomous navigation with LangGraph
    - 📊 Benchmarking against traditional crawlers
    - 🎥 Live vision feed and observability
    - 📈 Comprehensive metrics tracking
    
    **Tech Stack:**
    - Python, Playwright, LangChain/LangGraph
    - OpenAI GPT-4o / Google Gemini
    - Streamlit, Plotly
    - Scrapy, Beautiful Soup
    """)


def main():
    """Main application."""
    initialize_session_state()
    render_header()
    
    mode = render_sidebar()
    
    if mode == "Live Vision Feed":
        render_live_vision_feed()
    elif mode == "Benchmark Duel":
        render_benchmark_duel()
    elif mode == "Metrics Dashboard":
        render_metrics_dashboard()
    elif mode == "Configure":
        render_configure()


if __name__ == "__main__":
    main()
