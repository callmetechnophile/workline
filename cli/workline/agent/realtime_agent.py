"""
WorklineRealtimeAgent: Dedicated realtime agent for LiveKit voice and conversational interaction.
Maintains live multi-turn context (active project, current subsystem, recent retrievals)
and dynamically queries ProjectRetriever through Moss without dumping the whole project.
Produces concise spoken responses with verifiable .wl file citations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

from cli.workline.config.config import WorklineCLIConfig
from cli.workline.retrieval.context import ContextBuilder
from cli.workline.retrieval.record import EngineeringRecord
from cli.workline.retrieval.retriever import ProjectRetriever


@dataclass
class LiveSessionContext:
    """Ephemeral multi-turn live conversation context."""
    project_id: str
    project_root: str
    current_subsystem: Optional[str] = None
    turn_count: int = 0
    recent_queries: List[str] = field(default_factory=list)
    recent_sources: List[str] = field(default_factory=list)
    recent_records: List[EngineeringRecord] = field(default_factory=list)
    recent_tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class WorklineRealtimeAgent:
    """
    Dedicated WORKLINE Realtime Agent.
    Operates over the .wl filesystem using ProjectRetriever as its sole retrieval gateway.
    Never invents facts; always grounds responses in retrieved project documents.
    """

    def __init__(
        self,
        project_root: Path,
        retriever: Optional[ProjectRetriever] = None,
        config: Optional[WorklineCLIConfig] = None,
    ):
        self.project_root = project_root.resolve()
        self.retriever = retriever or ProjectRetriever(self.project_root)
        self.config = config or WorklineCLIConfig.load(self.project_root)
        
        # Read project identity
        from cli.workline.project.readme import parse_readme_wl
        readme_file = self.project_root / "README.wl"
        pid = "PROJ-UNKNOWN"
        if readme_file.exists():
            try:
                pid = parse_readme_wl(readme_file).project_id
            except Exception:
                pass

        self.context = LiveSessionContext(
            project_id=pid,
            project_root=str(self.project_root),
        )

    def process_realtime_input(self, user_utterance: str, speaker_role: str = "human") -> Dict[str, Any]:
        """
        Process user speech or text input.
        Extracts intent, updates subsystem context, retrieves relevant Moss records,
        and generates a concise, spoken-friendly answer with citations.
        """
        self.context.turn_count += 1
        self.context.recent_queries.append(user_utterance)
        
        # 1. Update live subsystem context from utterance if mentioned
        self._update_active_subsystem(user_utterance)

        # 2. Build augmented query taking active subsystem into account for follow-ups
        augmented_query = self._build_contextual_query(user_utterance)

        # 3. Dynamic context retrieval through ProjectRetriever (Local Moss)
        builder = ContextBuilder(default_token_budget=2000)
        bundle = builder.build_context(self.retriever, query=augmented_query, top_k=8)
        
        self.context.recent_records = bundle.records
        self.context.recent_sources = bundle.sources

        # 4. Generate spoken-friendly, project-grounded answer
        answer_text, sources = self._synthesize_spoken_response(user_utterance, bundle)

        # 5. Record conversation turn
        self.context.conversation_history.append({
            "speaker": speaker_role,
            "text": user_utterance,
            "agent_response": answer_text,
            "sources": sources,
        })

        return {
            "answer": answer_text,
            "sources": sources,
            "active_subsystem": self.context.current_subsystem,
            "project_id": self.context.project_id,
            "turn": self.context.turn_count,
        }

    def _update_active_subsystem(self, text: str) -> None:
        """Detect and set active engineering subsystem from user input."""
        t_low = text.lower()
        subsystems = ["power", "thermal", "compute", "sensors", "telemetry", "navigation", "mechanical", "pcb", "firmware"]
        for sub in subsystems:
            if sub in t_low:
                self.context.current_subsystem = sub
                break

    def _build_contextual_query(self, utterance: str) -> str:
        """Enrich short follow-up questions with recent subsystem context."""
        u_low = utterance.lower()
        # If user asks anaphoric questions ("why did we choose it?", "what about the regulator?", "what is the cost?")
        if len(utterance.split()) <= 6 or any(w in u_low for w in ("it", "this", "that", "why", "regulator", "selected")):
            if self.context.current_subsystem:
                return f"{utterance} {self.context.current_subsystem}"
        return utterance

    def _synthesize_spoken_response(
        self,
        utterance: str,
        bundle: Any,
    ) -> tuple[str, List[str]]:
        """
        Synthesize concise spoken-friendly response with clear file citations.
        """
        records = bundle.records
        if not records:
            return (
                f"I checked the {self.context.project_id} project files, but could not find specifications matching your query.",
                [],
            )

        u_low = utterance.lower()
        top = records[0]
        
        # Follow-up "Why did we select it?"
        if any(w in u_low for w in ("why", "reason", "choose", "select")):
            decisions = [r for r in records if r.resource_type in ("decision", "component")]
            if decisions:
                d = decisions[0]
                lines = [l.strip() for l in d.content.splitlines() if ":" in l and not l.strip().startswith("#")]
                summary = " ".join(lines[:3])
                ans = f"According to {d.path}, {summary}"
                sources = [d.path]
            else:
                ans = f"Based on {top.path}, {top.title} is specified for this subsystem."
                sources = [top.path]

        # Component / Regulator query
        elif any(w in u_low for w in ("regulator", "component", "what", "which", "sensor", "mcu", "controller")):
            comp_records = [r for r in records if r.resource_type in ("component", "bom")]
            if comp_records:
                c = comp_records[0]
                mpn = c.metadata.get("mpn") or c.title
                category = c.metadata.get("category", "component")
                manufacturer = c.metadata.get("manufacturer", "")
                mfg_str = f" from {manufacturer}" if manufacturer else ""
                ans = f"The current design specifies the {mpn} {category}{mfg_str}."
                sources = list({r.path for r in comp_records[:3]})
            else:
                ans = f"The design specifies {top.title} ({top.resource_type}) for this subsystem."
                sources = [top.path]

        # Overview query (Tell me about the power system)
        elif any(w in u_low for w in ("tell", "how", "overview", "system", "architecture")):
            arch = [r for r in records if r.resource_type in ("architecture", "requirement", "analysis")]
            useful = arch if arch else records[:2]
            parts = [f"In {r.path}: {r.title}" for r in useful[:2]]
            ans = f"The system architecture incorporates {len(records)} relevant modules: " + "; ".join(parts) + "."
            sources = list({r.path for r in useful})

        else:
            ans = f"Found relevant engineering records in {top.path} regarding {top.title}."
            sources = [top.path]

        # Add explicit Sources block
        if sources:
            src_block = "\n\nSources:\n" + "\n".join(f"- {s}" for s in sorted(set(sources)))
            full_response = ans + src_block
        else:
            full_response = ans

        return full_response, sorted(set(sources))
