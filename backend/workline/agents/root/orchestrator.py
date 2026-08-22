"""Root Workline Orchestrator: Coordinates planning, research, human decision checkpoints, and builder trees."""

from typing import Any, Dict, List, Optional
from backend.workline.agents.builder.builder_agent import BuilderAgent
from backend.workline.agents.planning.domain_researcher import DomainResearcherAgent
from backend.workline.agents.planning.timeline_agent import TimelineAgent
from backend.workline.agents.research.innovation_agent import InnovationAgent
from backend.workline.agents.research.research_agent import ResearchAgent
from backend.workline.agents.shared.context import build_agent_context
from backend.workline.agents.shared.prompts import ROOT_ORCHESTRATOR_PROMPT
from backend.workline.agents.shared.schemas import AgentFinding, AgentOutput
from backend.workline.agents.shared.state import AgentEvent, AgentState, AgentStatus
from backend.workline.agents.shared.tools import WorklineToolSuite


class RootOrchestratorAgent:
    """
    Root Workline Orchestrator.
    Directs workflow across Planning, Research, Human Checkpoints, and Builder Trees.
    """

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.name = "root_orchestrator"
        self.prompt = ROOT_ORCHESTRATOR_PROMPT

        # Sub-tree instances
        self.domain_researcher = DomainResearcherAgent(self.tools)
        self.timeline_agent = TimelineAgent(self.tools)
        self.research_agent = ResearchAgent(self.tools)
        self.innovation_agent = InnovationAgent(self.tools)
        self.builder_agent = BuilderAgent(self.tools)

    async def execute_phase1_planning_and_research(
        self, project_id: str, task: str, state: AgentState
    ) -> AgentOutput:
        """Run Planning and Research trees and pause at the Human Decision Checkpoint."""
        context = await build_agent_context(project_id=project_id, stage="ideation", task=task)
        findings: List[AgentFinding] = []
        phase_data: Dict[str, Any] = {}

        # 1. Domain Researcher
        state.agent_id = "domain_researcher"
        state.stage = "requirements_definition"
        state.events.append(AgentEvent(agent_id=state.agent_id, event_type="STATE_CHANGE", summary="Running Domain Researcher"))
        domain_out = await self.domain_researcher.execute(project_id, context)
        findings.extend(domain_out.findings)
        phase_data["domain"] = domain_out.data

        # 2. Timeline Agent
        state.agent_id = "timeline_agent"
        state.stage = "project_planning"
        state.events.append(AgentEvent(agent_id=state.agent_id, event_type="STATE_CHANGE", summary="Running Timeline Agent"))
        timeline_out = await self.timeline_agent.execute(project_id, context)
        findings.extend(timeline_out.findings)
        phase_data["timeline"] = timeline_out.data

        # 3. Research Agent
        state.agent_id = "research_agent"
        state.stage = "literature_research"
        state.events.append(AgentEvent(agent_id=state.agent_id, event_type="STATE_CHANGE", summary="Running Research Agent"))
        research_out = await self.research_agent.execute(project_id, context)
        findings.extend(research_out.findings)
        phase_data["research"] = research_out.data

        # 4. Innovation Agent
        state.agent_id = "innovation_agent"
        state.stage = "innovation_synthesis"
        state.events.append(AgentEvent(agent_id=state.agent_id, event_type="STATE_CHANGE", summary="Running Innovation Agent"))
        innov_out = await self.innovation_agent.execute(project_id, context)
        findings.extend(innov_out.findings)
        phase_data["innovation"] = innov_out.data

        # Update lifecycle state in SurrealDB
        await self.tools.update_project_state(project_id, {"lifecycle_stage": "research_complete"})

        # Human Decision Checkpoint
        state.agent_id = "root_orchestrator"
        state.stage = "research_complete"
        state.status = AgentStatus.WAITING_FOR_USER
        state.requires_user_action = True
        state.action_prompt = "RESEARCH COMPLETE. Choose: [Continue Research] or [Start Building]"
        state.events.append(
            AgentEvent(
                agent_id=self.name,
                event_type="DECISION_REQUIRED",
                summary="Reached Human Decision Checkpoint (RESEARCH COMPLETE)",
                details={"options": ["CONTINUE_RESEARCH", "START_BUILD"]},
            )
        )

        return AgentOutput(
            agent=self.name,
            status=AgentStatus.WAITING_FOR_USER.value,
            stage="research_complete",
            summary="Research and planning phase completed. Waiting for user decision to continue research or start building.",
            findings=findings,
            requires_user_action=True,
            action_prompt="RESEARCH COMPLETE. Choose: [Continue Research] or [Start Building]",
            data=phase_data,
        )

    async def execute_phase2_builder(
        self, project_id: str, task: str, state: AgentState
    ) -> AgentOutput:
        """Resume execution following human approval and run Builder Tree."""
        state.agent_id = "builder_agent"
        state.stage = "hardware_build"
        state.status = AgentStatus.RUNNING
        state.requires_user_action = False
        state.events.append(AgentEvent(agent_id=state.agent_id, event_type="STATE_CHANGE", summary="Starting Builder Sub-Tree"))

        context = await build_agent_context(project_id=project_id, stage="hardware_build", task=task)
        builder_out = await self.builder_agent.execute(project_id, context)

        state.agent_id = "root_orchestrator"
        state.stage = "hardware_build_complete"
        state.status = AgentStatus.COMPLETED
        state.output_summary = builder_out.summary
        state.events.append(AgentEvent(agent_id=self.name, event_type="SUMMARY", summary=builder_out.summary))

        return builder_out
