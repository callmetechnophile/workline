"""
Workline R2 - AI, Research & Multi-Agent Orchestration Service
Standalone microservice for Deep Research, OmniRoute agent pipelines,
multimodal generation, and LLM reasoning.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.research import router as research_router
from backend.workline.api.agents import router as workline_agents_router
from backend.workline.api.generation import router as generation_router
from backend.workline.api.cache import router as cache_router
from backend.routes.speech import router as speech_router

app = FastAPI(
    title="Workline R2 - AI & Research Agents Service",
    description="Dedicated microservice for deep research, OmniRoute multi-agent workflows, and synthesis.",
    version="1.0.0-rc1",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI & Agent Routers
app.include_router(research_router)
app.include_router(workline_agents_router)
app.include_router(generation_router)
app.include_router(cache_router)
app.include_router(speech_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health endpoint for R2 AI/Research service."""
    return {
        "status": "healthy",
        "service": "workline-ai-agents",
        "version": "1.0.0-rc1",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.services.ai.main:app", host="0.0.0.0", port=10002, reload=True)
