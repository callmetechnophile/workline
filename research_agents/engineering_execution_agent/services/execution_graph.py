"""
Machine-readable execution graph builder (Section 54).
Constructs Nodes and Edges capturing the complete authority-to-execution lineage.
"""

from typing import Any, Dict, List
from research_agents.engineering_execution_agent.schemas import (
    AuthorizedExecution,
    EngineeringExecutionContext,
    ExecutionGraph,
    ExecutionGraphEdge,
    ExecutionGraphNode,
    ToolCallRecord,
)


class ExecutionGraphBuilder:
    """Constructs verifiable execution lineage graphs (Section 54)."""

    def build_graph(
        self,
        context: EngineeringExecutionContext,
        auth: AuthorizedExecution,
        completed_tasks: List[Dict[str, Any]],
        failed_tasks: List[Dict[str, Any]],
        tool_calls: List[ToolCallRecord],
    ) -> ExecutionGraph:
        nodes: List[ExecutionGraphNode] = []
        edges: List[ExecutionGraphEdge] = []

        # 1. User & Agent Nodes
        nodes.append(ExecutionGraphNode(id=context.user_id, type="user", label="Project Owner"))
        nodes.append(ExecutionGraphNode(id=context.agent_id, type="agent", label="EngineeringExecutionAgent"))
        if context.parent_agent_id:
            nodes.append(ExecutionGraphNode(id=context.parent_agent_id, type="agent", label="Parent Orchestrator"))
            edges.append(ExecutionGraphEdge(source=context.user_id, target=context.parent_agent_id, relation="authorized_by"))
            edges.append(ExecutionGraphEdge(source=context.parent_agent_id, target=context.agent_id, relation="delegated_to"))
        else:
            edges.append(ExecutionGraphEdge(source=context.user_id, target=context.agent_id, relation="authorized_by"))

        # 2. Authorization Node
        nodes.append(ExecutionGraphNode(id=auth.authorization_id, type="authorization", label="ArmorIQ Authorization"))
        edges.append(ExecutionGraphEdge(source=context.agent_id, target=auth.authorization_id, relation="executes"))

        # 3. Task & Tool Call Nodes
        all_tasks = completed_tasks + failed_tasks
        for t in all_tasks:
            t_id = t.get("task_id", "TASK-001")
            nodes.append(ExecutionGraphNode(id=t_id, type="task", label=t.get("title", t_id), metadata={"status": t.get("status")}))
            edges.append(ExecutionGraphEdge(source=auth.authorization_id, target=t_id, relation="authorizes"))

        for tc in tool_calls:
            nodes.append(ExecutionGraphNode(id=tc.tool_call_id, type="tool", label=tc.tool, metadata={"operation": tc.operation, "status": tc.status}))
            edges.append(ExecutionGraphEdge(source=tc.task_id, target=tc.tool_call_id, relation="invokes"))
            if tc.armoriq_receipt_id:
                nodes.append(ExecutionGraphNode(id=tc.armoriq_receipt_id, type="receipt", label="ArmorIQ Receipt"))
                edges.append(ExecutionGraphEdge(source=tc.tool_call_id, target=tc.armoriq_receipt_id, relation="verified_by"))

        return ExecutionGraph(nodes=nodes, edges=edges)
