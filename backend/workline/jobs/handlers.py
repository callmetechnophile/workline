"""
Standard job handlers registering heavy compute tasks with JobRegistry.
"""

from typing import Any, Dict
from loguru import logger
from backend.workline.jobs import Job, default_job_registry


async def handle_pcb_simulation_job(job: Job) -> Dict[str, Any]:
    """Execute asynchronous PCB thermal/physics simulation."""
    logger.info(f"[JobHandler] Starting async simulation for project {job.project_id}")
    from backend.services.thermal_service import calculate_project_thermal_analysis
    components = job.input_reference.get("components", [])
    result = calculate_project_thermal_analysis(components=components, project_id=job.project_id or "default")
    return {"simulation_result": result, "status": "COMPLETED"}


async def handle_procurement_search_job(job: Job) -> Dict[str, Any]:
    """Execute asynchronous multi-vendor procurement search."""
    logger.info(f"[JobHandler] Starting async procurement search for project {job.project_id}")
    from backend.workline.procurement.search import default_procurement_engine
    mpns = job.input_reference.get("mpns", [])
    quotes = await default_procurement_engine.search_multiple(mpns)
    return {"quotes": [q.model_dump() for q in quotes], "count": len(quotes)}


# Register standard handlers
default_job_registry.register("pcb_simulation", handle_pcb_simulation_job)
default_job_registry.register("procurement_search", handle_procurement_search_job)
