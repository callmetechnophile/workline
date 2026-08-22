"""
Workline R6 - CLI Distribution & Release Metadata Service
Provides CLI update manifests, version resolution, release metadata,
and package verification hashes for the wline client.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

try:
    from cli.wline import __version__ as cli_current_version
except (ImportError, ModuleNotFoundError):
    cli_current_version = "1.0.0-rc1"

app = FastAPI(
    title="Workline R6 - CLI Release & Distribution Service",
    description="Dedicated service managing CLI release manifests, binary update checksums, and client diagnostics.",
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


@app.get("/health", tags=["Health"])
async def health_check():
    """Health endpoint for R6 CLI Distribution service."""
    return {
        "status": "healthy",
        "service": "workline-cli-distribution",
        "version": "1.0.0-rc1",
    }


@app.get("/api/cli/version", tags=["CLI Distribution"])
async def get_cli_version():
    """Return the latest recommended CLI version and minimum supported version."""
    return {
        "latest_version": cli_current_version,
        "minimum_supported_version": "0.1.0",
        "release_tag": f"v{cli_current_version}",
        "release_url": "https://github.com/callmetechnophile/workline/releases",
    }


@app.get("/api/cli/manifest", tags=["CLI Distribution"])
async def get_cli_manifest():
    """Return full update manifest with install commands and checksums."""
    return {
        "package_name": "workline",
        "executable": "wline",
        "version": cli_current_version,
        "install_methods": {
            "pip": f"pip install workline=={cli_current_version}",
            "pipx": f"pipx install workline=={cli_current_version}",
            "git": "git clone https://github.com/callmetechnophile/workline.git && pip install -e .",
        },
        "platforms": ["windows-amd64", "linux-amd64", "darwin-arm64", "darwin-amd64"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.services.cli.main:app", host="0.0.0.0", port=10006, reload=True)
