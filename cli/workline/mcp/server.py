"""
MCP (Model Context Protocol) tool exposure for WORKLINE projects.
Exposes project search, context retrieval, component lookup, and BOM inspection
to external AI agents via clean tool interfaces.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from cli.workline.retrieval.context import ContextBuilder
from cli.workline.retrieval.retriever import ProjectRetriever


class WorklineMCPServer:
    """MCP interface exposing WORKLINE project context tools."""

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.retriever = ProjectRetriever(self.project_root)
        self.context_builder = ContextBuilder()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return MCP tool schemas for registration with external agents."""
        return [
            {
                "name": "workline_search",
                "description": "Perform local hybrid semantic search over WORKLINE project files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Natural language or technical search query"},
                        "resource_type": {"type": "string", "description": "Optional filter (component, requirement, architecture, etc.)"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "workline_context",
                "description": "Retrieve focused multi-domain engineering context bundle for a query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Engineering topic or subsystem inquiry"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "workline_component_lookup",
                "description": "Look up component dossier by Manufacturer Part Number (MPN).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mpn": {"type": "string", "description": "Manufacturer Part Number"},
                    },
                    "required": ["mpn"],
                },
            },
        ]

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch MCP tool execution."""
        if name == "workline_search":
            query = arguments.get("query", "")
            rtype = arguments.get("resource_type")
            records = self.retriever.retrieve(query, top_k=10, resource_types=[rtype] if rtype else None)
            return {"results": [r.to_dict() for r in records]}
            
        elif name == "workline_context":
            query = arguments.get("query", "")
            bundle = self.context_builder.build_context(self.retriever, query)
            return {
                "context": bundle.formatted_context,
                "sources": bundle.sources,
                "estimated_tokens": bundle.estimated_tokens,
            }
            
        elif name == "workline_component_lookup":
            mpn = arguments.get("mpn", "")
            record = self.retriever.lookup_component(mpn)
            return {"component": record.to_dict() if record else None}
            
        raise ValueError(f"Unknown MCP tool: {name}")
