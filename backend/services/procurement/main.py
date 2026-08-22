"""
Workline R5 - Procurement & Collaboration Microservice
Standalone entrypoint for BOM management, multi-supplier quote resolution,
x402 payment verification, and calendar integration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.workline.api.bom import router as bom_router
from backend.workline.api.procurement import router as procurement_router
from backend.workline.api.orders import router as orders_router
from backend.workline.api.payments import router as payments_router
from backend.workline.api.git import router as git_router
from backend.routes.calendar import router as calendar_router

app = FastAPI(
    title="Workline R5 - Procurement & Collaboration Service",
    description="Dedicated microservice for BOM optimization, supplier quotes, x402 payments, and scheduling.",
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

# Include Procurement & Collaboration Routers
app.include_router(bom_router)
app.include_router(procurement_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(git_router)
app.include_router(calendar_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health endpoint for Render and orchestrator probes."""
    return {
        "status": "healthy",
        "service": "workline-procurement",
        "version": "1.0.0-rc1",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.services.procurement.main:app", host="0.0.0.0", port=10005, reload=True)
