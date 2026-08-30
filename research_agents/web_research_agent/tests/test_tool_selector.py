"""
Unit tests for deterministic tool selection policy (Tavily vs. Anakin vs. Agent #1 delegation).
"""

from research_agents.web_research_agent.services.tool_selector import ToolSelector


def test_tool_selector_broad_search():
    selector = ToolSelector()
    choice, reason = selector.select_tool(
        task_intent="find engineering sources",
        query="Jetson Orin Nano thermal vision ROS2",
    )
    assert choice == "tavily_search"
    assert "Tavily" in reason


def test_tool_selector_scrape_vendor_url():
    selector = ToolSelector()
    choice, reason = selector.select_tool(
        task_intent="extract component specs",
        target_url="https://www.ti.com/product/TPS54308",
    )
    assert choice == "anakin_scrape"
    assert "Anakin" in reason


def test_tool_selector_crawl_documentation():
    selector = ToolSelector()
    choice, reason = selector.select_tool(
        task_intent="crawl documentation website",
        target_url="https://docs.px4.io/main/en/",
    )
    assert choice == "anakin_crawl"
    assert "crawl" in reason.lower()


def test_tool_selector_delegate_academic():
    selector = ToolSelector()
    choice, reason = selector.select_tool(
        task_intent="find academic research",
        query="arXiv 2405.10123 peer reviewed paper on thermal UAV",
    )
    assert choice == "delegate_academic"
    assert "Agent #1" in reason or "ResearchPaperAgent" in reason
