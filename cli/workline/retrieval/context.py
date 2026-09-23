"""
ContextBuilder for WORKLINE AI agent and CLI.
Retrieves, ranks, deduplicates, and formats project context within strict token budgets.
Produces verifiable source citations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from cli.workline.retrieval.record import EngineeringRecord
from cli.workline.retrieval.retriever import ProjectRetriever


@dataclass
class ContextBundle:
    """Formatted context bundle with provenance and token budgeting."""
    query: str
    records: List[EngineeringRecord] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    sections: Dict[str, List[str]] = field(default_factory=dict)
    formatted_context: str = ""
    estimated_tokens: int = 0


def _estimate_tokens(text: str) -> int:
    """Rough estimation of token count (~4 chars per token)."""
    return len(text) // 4 + 1


class ContextBuilder:
    """Constructs focused LLM context from retrieved engineering records."""

    def __init__(self, default_token_budget: int = 3500):
        self.default_token_budget = default_token_budget

    def build_context(
        self,
        retriever: ProjectRetriever,
        query: str,
        token_budget: Optional[int] = None,
        top_k: int = 12,
    ) -> ContextBundle:
        """
        Query ProjectRetriever, group by domain sections, prune within token budget,
        and attach verifiable file citations.
        """
        budget = token_budget or self.default_token_budget
        
        # Retrieve across diverse engineering types
        records = retriever.retrieve(
            query=query,
            top_k=top_k,
            resource_types=[
                "architecture",
                "requirement",
                "component",
                "bom",
                "analysis",
                "decision",
                "research",
                "task",
                "project",
            ],
        )

        sources: List[str] = []
        seen_paths: Set[str] = set()
        sections: Dict[str, List[str]] = {}
        
        for r in records:
            if r.path and r.path not in seen_paths:
                seen_paths.add(r.path)
                sources.append(r.path)
                
            sec_name = r.resource_type.upper()
            if sec_name not in sections:
                sections[sec_name] = []
                
            snippet = r.content.strip()
            # Trim large single file contents
            if len(snippet) > 800:
                snippet = snippet[:800] + "... [trimmed]"
            sections[sec_name].append(f"[{r.path}]\n{snippet}")

        # Construct structured context document within budget
        lines = [
            f"=== WORKLINE PROJECT CONTEXT ===",
            f"Query: {query}",
            "",
        ]
        
        current_tokens = _estimate_tokens("\n".join(lines))
        
        # Priority order for engineering context sections
        order = ["PROJECT", "ARCHITECTURE", "REQUIREMENT", "COMPONENT", "BOM", "ANALYSIS", "DECISION", "RESEARCH", "TASK"]
        
        for sec in order:
            if sec in sections and sections[sec]:
                lines.append(f"## {sec}")
                for entry in sections[sec]:
                    entry_tokens = _estimate_tokens(entry)
                    if current_tokens + entry_tokens > budget:
                        lines.append("... [Context budget reached]")
                        break
                    lines.append(entry)
                    lines.append("")
                    current_tokens += entry_tokens
                    
        lines.append("## SOURCES")
        for s in sources:
            lines.append(f"- {s}")
            
        formatted = "\n".join(lines)
        
        return ContextBundle(
            query=query,
            records=records,
            sources=sources,
            sections=sections,
            formatted_context=formatted,
            estimated_tokens=_estimate_tokens(formatted),
        )
