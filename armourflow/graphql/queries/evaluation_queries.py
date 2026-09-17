"""
Platform evaluation harness benchmark GraphQL query resolvers.
"""

from typing import List, Optional
import strawberry
from strawberry.types import Info
from armourflow.evals import get_evaluation_harness
from armourflow.graphql.types.evaluation import (
    PlatformHarnessReportType,
    AgentEvalSummaryType,
    BenchmarkScoreType,
)


@strawberry.type
class EvaluationQueries:
    @strawberry.field
    async def evaluation_report(self, info: Info) -> PlatformHarnessReportType:
        """Retrieve latest platform evaluation benchmark report."""
        harness = get_evaluation_harness()
        rep = await harness.run_platform_benchmarks()

        summaries = []
        for aid, s in rep.agent_summaries.items():
            b_list = [
                BenchmarkScoreType(
                    benchmark_id=b.benchmark_id,
                    name=b.name,
                    category=b.category,
                    passed=b.passed,
                    details=b.details,
                )
                for b in s.benchmarks
            ]
            summaries.append(
                AgentEvalSummaryType(
                    agent_id=s.agent_id,
                    total_benchmarks=s.total_benchmarks,
                    passed_benchmarks=s.passed_benchmarks,
                    score_percentage=s.score_percentage,
                    benchmarks=b_list,
                )
            )

        return PlatformHarnessReportType(
            timestamp=rep.timestamp,
            total_agents_evaluated=rep.total_agents_evaluated,
            total_benchmarks=rep.total_benchmarks,
            total_passed=rep.total_passed,
            overall_pass_rate=rep.overall_pass_rate,
            agent_summaries=summaries,
        )

    @strawberry.field
    async def agent_evaluation(self, info: Info, agent_id: str) -> Optional[AgentEvalSummaryType]:
        """Run or inspect benchmark evaluation for a specific agent."""
        harness = get_evaluation_harness()
        s = await harness.evaluate_agent(agent_id)
        if not s:
            return None

        b_list = [
            BenchmarkScoreType(
                benchmark_id=b.benchmark_id,
                name=b.name,
                category=b.category,
                passed=b.passed,
                details=b.details,
            )
            for b in s.benchmarks
        ]
        return AgentEvalSummaryType(
            agent_id=s.agent_id,
            total_benchmarks=s.total_benchmarks,
            passed_benchmarks=s.passed_benchmarks,
            score_percentage=s.score_percentage,
            benchmarks=b_list,
        )
