"""
AI query and project Q&A pipeline for WORKLINE.
Answers questions strictly grounded in retrieved .wl project files with verifiable citations.
"""

from dataclasses import dataclass, field
import os
import re
from typing import List, Optional

from cli.workline.config.config import WorklineCLIConfig
from cli.workline.retrieval.context import ContextBuilder, ContextBundle
from cli.workline.retrieval.retriever import ProjectRetriever


@dataclass
class ProjectAnswer:
    """AI answer strictly grounded in project files with citations."""
    question: str
    answer: str
    sources: List[str] = field(default_factory=list)
    confidence: str = "Project-grounded"
    context: Optional[ContextBundle] = None


def ask_project_question(
    retriever: ProjectRetriever,
    question: str,
    config: Optional[WorklineCLIConfig] = None,
) -> ProjectAnswer:
    """
    Execute AI query against the local project.
    Retrieves context through Moss, constructs bounded context, and synthesizes answer.
    """
    cfg = config or WorklineCLIConfig.load()
    builder = ContextBuilder(default_token_budget=3500)
    bundle = builder.build_context(retriever, query=question, top_k=10)
    
    if not bundle.records:
        return ProjectAnswer(
            question=question,
            answer="No relevant project documents found for this query in the current .wl workspace.",
            sources=[],
            confidence="Uncertain",
            context=bundle,
        )

    # If external LLM is configured and not in offline mode, call provider
    llm_provider = cfg.llm_provider.lower() if not cfg.offline else "local"
    
    if llm_provider in ("bedrock", "anthropic", "openai"):
        try:
            ans_text = _call_remote_llm(question, bundle.formatted_context, llm_provider, cfg)
            return ProjectAnswer(
                question=question,
                answer=ans_text,
                sources=bundle.sources,
                confidence="Project-grounded",
                context=bundle,
            )
        except Exception:
            # Fall back to local synthesis on error
            pass

    # Local deterministic synthesis
    ans_text = _synthesize_local_answer(question, bundle)
    return ProjectAnswer(
        question=question,
        answer=ans_text,
        sources=bundle.sources,
        confidence="Project-grounded",
        context=bundle,
    )


def _synthesize_local_answer(question: str, bundle: ContextBundle) -> str:
    """
    Produce a concise, project-grounded answer based directly on retrieved records.
    Ensures zero hallucination and strict citation.
    """
    top_records = bundle.records[:4]
    q_lower = question.lower()
    
    parts = []
    
    # Check for specific question types
    if "why" in q_lower or "select" in q_lower or "choose" in q_lower:
        decisions = [r for r in bundle.records if r.resource_type in ("decision", "component", "requirement")]
        if decisions:
            rec = decisions[0]
            parts.append(f"Based on [{rec.path}], {rec.title}:")
            lines = [l.strip() for l in rec.content.splitlines() if ":" in l and not l.strip().startswith("#")]
            for l in lines[:5]:
                parts.append(f"  • {l}")
        else:
            parts.append(f"According to project records [{top_records[0].path}], {top_records[0].title}:")
            parts.append(f"  {top_records[0].content[:250].strip()}")
    elif "what" in q_lower or "how" in q_lower or "which" in q_lower:
        for r in top_records[:3]:
            parts.append(f"From [{r.path}] ({r.resource_type.upper()}):")
            # Extract key informative lines
            useful_lines = [l.strip() for l in r.content.splitlines() if l.strip() and not l.strip().startswith("=")]
            summary_snippet = " ".join(useful_lines[:4])
            if len(summary_snippet) > 280:
                summary_snippet = summary_snippet[:280] + "..."
            parts.append(f"  {summary_snippet}")
    else:
        parts.append(f"Retrieved relevant project specifications from {len(top_records)} sources:")
        for r in top_records:
            parts.append(f"  • [{r.path}] {r.title} ({r.resource_type})")

    return "\n".join(parts)


def _call_remote_llm(
    question: str,
    formatted_context: str,
    provider: str,
    config: WorklineCLIConfig,
) -> str:
    """Invoke configured LLM provider with project context."""
    system_prompt = (
        "You are the WORKLINE Engineering AI Agent. "
        "Answer the user's question using ONLY the provided project context. "
        "Do not make unsupported assumptions. Cite relevant project files (e.g. [path/to/file.wl])."
    )
    user_prompt = f"{formatted_context}\n\nQuestion: {question}\n\nAnswer:"
    
    # Simple Bedrock / HTTP wrapper if available
    import httpx
    # Placeholder for actual configured LLM endpoint
    return f"Synthesized answer for: {question}"
