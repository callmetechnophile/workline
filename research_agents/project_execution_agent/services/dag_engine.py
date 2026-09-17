"""Task Dependency DAG and Critical Path solver engine (Agent #10)."""
from collections import defaultdict, deque
from typing import Dict, List
from research_agents.project_execution_agent.schemas import DependencyDAG, PlanningTask

class DAGEngine:
    """Builds and validates task dependency graphs, checks for circular dependencies, and calculates critical paths."""

    def build_dag(self, tasks: List[PlanningTask]) -> DependencyDAG:
        nodes = [t.task_id for t in tasks]
        node_set = set(nodes)
        edges: List[Dict[str, str]] = []
        adj: Dict[str, List[str]] = defaultdict(list)
        in_degree: Dict[str, int] = {n: 0 for n in nodes}
        
        for t in tasks:
            for dep in t.dependencies:
                if dep in node_set:
                    edges.append({"from": dep, "to": t.task_id})
                    adj[dep].append(t.task_id)
                    in_degree[t.task_id] += 1

        queue = deque([n for n, deg in in_degree.items() if deg == 0])
        topo_order: List[str] = []
        
        while queue:
            curr = queue.popleft()
            topo_order.append(curr)
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        has_cycle = len(topo_order) != len(nodes)
        cycle_nodes = [n for n, deg in in_degree.items() if deg > 0] if has_cycle else []

        task_map = {t.task_id: t for t in tasks}
        dist: Dict[str, float] = {n: task_map[n].estimated_hours for n in nodes}
        parent: Dict[str, str] = {}

        if not has_cycle:
            for u in topo_order:
                for v in adj[u]:
                    weight = task_map[v].estimated_hours
                    if dist[u] + weight > dist[v]:
                        dist[v] = dist[u] + weight
                        parent[v] = u

            if dist:
                max_node = max(dist, key=dist.get)
                curr = max_node
                crit_path = []
                while curr:
                    crit_path.append(curr)
                    curr = parent.get(curr)
                crit_path.reverse()
            else:
                crit_path = []
        else:
            crit_path = []

        return DependencyDAG(
            nodes=nodes,
            edges=edges,
            topological_order=topo_order if not has_cycle else [],
            critical_path=crit_path,
            has_cycle=has_cycle,
            cycle_nodes=cycle_nodes,
        )
