"""
Change invalidation and re-optimization planning engine for EngineeringOptimizationAgent.
Detects upstream BOM/architecture changes and marks affected optimization results as STALE or INVALIDATED.
"""

from typing import Dict, List, Optional
from loguru import logger

from research_agents.engineering_optimization.schemas import OptimizationObject


class ReoptimizationEngine:
    """
    Detects when an upstream change (BOM version bump, architecture revision) invalidates
    existing optimization results and prepares a re-optimization recommendation.

    INVARIANTS:
    - Never silently drop a stale status. Always surface STALE or INVALIDATED explicitly.
    - Re-optimization does not automatically select any candidate. Human approval required.
    """

    def check_staleness(
        self,
        optimization: OptimizationObject,
        current_bom_version: str,
        current_architecture_version: str,
    ) -> bool:
        """Return True if the optimization is stale due to upstream version changes."""
        bom_changed = optimization.bom_version != current_bom_version
        arch_changed = optimization.architecture_version != current_architecture_version
        if bom_changed or arch_changed:
            logger.info(
                f"[REOPTIMIZATION] Optimization {optimization.optimization_id} is STALE: "
                f"BOM {optimization.bom_version}->{current_bom_version}, "
                f"Arch {optimization.architecture_version}->{current_architecture_version}"
            )
            return True
        return False

    def mark_stale(self, optimization: OptimizationObject) -> OptimizationObject:
        """Mark an optimization as STALE in memory."""
        optimization.status = "STALE"
        logger.info(f"[REOPTIMIZATION] Marked {optimization.optimization_id} as STALE")
        return optimization

    def mark_invalidated(self, optimization: OptimizationObject) -> OptimizationObject:
        """Mark an optimization as INVALIDATED (more severe than STALE)."""
        optimization.status = "INVALIDATED"
        logger.warning(
            f"[REOPTIMIZATION] Marked {optimization.optimization_id} as INVALIDATED — "
            "re-optimization required before this result can be used."
        )
        return optimization

    def suggest_reoptimization(
        self,
        optimization: OptimizationObject,
        reason: str,
    ) -> Dict:
        """Produce a re-optimization recommendation record."""
        return {
            "optimization_id": optimization.optimization_id,
            "project_id": optimization.project_id,
            "status": optimization.status,
            "reason": reason,
            "action": "RE_OPTIMIZE",
            "message": (
                f"Optimization {optimization.optimization_id} is {optimization.status} "
                f"due to: {reason}. Re-run optimization before selecting any candidate."
            ),
        }
