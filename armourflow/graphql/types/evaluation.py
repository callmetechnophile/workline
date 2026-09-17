"""
Evaluation harness and benchmark GraphQL types.
"""

from typing import List, Optional
import strawberry


@strawberry.type
class BenchmarkScoreType:
    benchmark_id: str
    name: str
    category: str
    passed: bool
    details: Optional[str] = None


@strawberry.type
class AgentEvalSummaryType:
    agent_id: str
    total_benchmarks: int
    passed_benchmarks: int
    score_percentage: float
    benchmarks: List[BenchmarkScoreType]


@strawberry.type
class PlatformHarnessReportType:
    timestamp: float
    total_agents_evaluated: int
    total_benchmarks: int
    total_passed: int
    overall_pass_rate: float
    agent_summaries: List[AgentEvalSummaryType]
