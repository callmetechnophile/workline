"""
Workline R4 - Engineering, Physics & Simulation Microservice
Dedicated microservice for PINN physics-informed neural surrogates, thermal modeling,
PCB DRC geometric validation, and architecture decision engines.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.packages import router as packages_router
from backend.workline.api.pcb import router as pcb_router
from backend.workline.validation.api import router as validation_router
from backend.workline.decision.api import router as decision_engine_router

app = FastAPI(
    title="Workline R4 - Engineering & Simulation Service",
    description="Dedicated microservice for PINN neural solvers, thermal simulation, and PCB geometric validation.",
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

# Engineering Routers
app.include_router(packages_router)
app.include_router(pcb_router)
app.include_router(validation_router)
app.include_router(decision_engine_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health endpoint for R4 Engineering/Simulation service."""
    return {
        "status": "healthy",
        "service": "workline-engineering-simulation",
        "version": "1.0.0-rc1",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.services.engineering.main:app", host="0.0.0.0", port=10004, reload=True)
