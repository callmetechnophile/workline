"""Implementation of `wg doctor` — full environment diagnostics."""

import socket
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import typer
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


# ── TCP port checks ───────────────────────────────────────────────────────────

def _tcp_check(host: str, port: int, timeout: float = 2.0) -> Tuple[bool, str]:
    """Return (reachable, message) for a TCP port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{host}:{port} reachable"
    except socket.timeout:
        return False, f"{host}:{port} timed out"
    except ConnectionRefusedError:
        return False, f"{host}:{port} connection refused (service not running)"
    except OSError as e:
        return False, f"{host}:{port} {e}"


def _http_check(url: str, timeout: float = 3.0) -> Tuple[bool, str]:
    """Return (ok, message) from an HTTP GET."""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status < 400, f"HTTP {resp.status}"
    except Exception as e:
        return False, str(e)


def _mark(ok: bool) -> str:
    return "[bold green]✓[/bold green]" if ok else "[bold red]✗[/bold red]"


def _warn(msg: str) -> str:
    return f"[bold yellow]⚠[/bold yellow] {msg}"


def doctor_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path to check"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to auto-fix minor issues"),
) -> None:
    """Run comprehensive WORKLINE environment diagnostics."""
    console.print("\n[bold white]WORKLINE DOCTOR[/bold white]\n")

    from cli.workline import __version__
    console.print(f"CLI version: [bold]{__version__}[/bold]")
    console.print(f"Python: [bold]{sys.version.split()[0]}[/bold]")
    console.print()

    target = Path(path).resolve() if path else Path.cwd()
    
    checks: list = []  # (label, ok, detail)

    # ── 1. CLI ───────────────────────────────────────────────────────────────
    console.print("[bold]CLI & Runtime[/bold]")
    checks.append(("CLI installed", True, f"wg v{__version__}"))
    py_ok = sys.version_info >= (3, 9)
    checks.append(("Python ≥ 3.9", py_ok, f"{sys.version.split()[0]}"))

    # Check key imports
    for pkg, import_name in [
        ("typer", "typer"),
        ("rich", "rich"),
        ("pydantic", "pydantic"),
        ("yaml", "yaml"),
    ]:
        try:
            __import__(import_name)
            checks.append((f"{pkg} available", True, ""))
        except ImportError:
            checks.append((f"{pkg} available", False, f"pip install {pkg}"))

    _print_checks(checks[-5:])
    checks_start = len(checks)

    # ── 2. Docker ────────────────────────────────────────────────────────────
    console.print("\n[bold]Docker[/bold]")
    docker_checks = []
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        docker_ok = result.returncode == 0
        docker_checks.append(("Docker daemon", docker_ok, "running" if docker_ok else "not running"))
    except FileNotFoundError:
        docker_checks.append(("Docker daemon", False, "docker not found in PATH"))
    except subprocess.TimeoutExpired:
        docker_checks.append(("Docker daemon", False, "timed out"))

    # Check compose file
    compose_file = _find_compose_file()
    docker_checks.append(("docker-compose.yml", compose_file is not None, str(compose_file) if compose_file else "not found"))
    _print_checks(docker_checks)
    checks.extend(docker_checks)

    # ── 3. Stack services ────────────────────────────────────────────────────
    console.print("\n[bold]WORKLINE Stack[/bold]")
    stack_checks = []

    api_ok, api_msg = _http_check("http://localhost:8000/health")
    stack_checks.append(("API (port 8000)", api_ok, api_msg))

    surreal_ok, surreal_msg = _tcp_check("localhost", 8001)
    stack_checks.append(("SurrealDB (port 8001)", surreal_ok, surreal_msg))

    # Deeper SurrealDB check if port open
    if surreal_ok:
        try:
            from backend.workline.database.surrealdb import surreal_db
            import asyncio
            connected = asyncio.run(surreal_db.connect()) if not surreal_db.is_connected() else True
            stack_checks.append(("SurrealDB auth", connected, "authenticated" if connected else "auth failed"))
        except Exception as e:
            stack_checks.append(("SurrealDB auth", False, str(e)[:60]))

    qdrant_ok, qdrant_msg = _http_check("http://localhost:6333/livez")
    stack_checks.append(("Qdrant (port 6333)", qdrant_ok, qdrant_msg))

    if qdrant_ok:
        try:
            from backend.workline.retrieval.qdrant import qdrant_manager
            import asyncio
            connected = asyncio.run(qdrant_manager.connect()) if not qdrant_manager.is_connected() else True
            stack_checks.append(("Qdrant collections", connected, "collections OK" if connected else "init failed"))
        except Exception as e:
            stack_checks.append(("Qdrant collections", False, str(e)[:60]))

    redis_ok, redis_msg = _tcp_check("localhost", 6379)
    stack_checks.append(("Redis (port 6379)", redis_ok, redis_msg))

    _print_checks(stack_checks)
    checks.extend(stack_checks)

    # ── 4. Project ───────────────────────────────────────────────────────────
    console.print("\n[bold]Project[/bold]")
    proj_checks = []

    from cli.workline.project.filesystem import find_project_root, WL_METADATA_DIR
    root = find_project_root(target)
    proj_checks.append(("Project detected", root is not None, str(root) if root else f"not found in {target}"))

    if root:
        readme_ok = (root / "README.wl").exists()
        proj_checks.append(("README.wl", readme_ok, ""))

        wl_dir = root / WL_METADATA_DIR
        wl_ok = wl_dir.exists()
        proj_checks.append((".wl/ directory", wl_ok, ""))

        manifest_ok = (wl_dir / "manifest.wl").exists()
        proj_checks.append((".wl/manifest.wl", manifest_ok, ""))

        # Validation
        try:
            from cli.workline.project.validator import validate_project
            result = validate_project(root, verify_checksums=False)
            proj_checks.append(("Project validation", result.is_valid, "; ".join(result.errors[:2]) if result.errors else "OK"))
        except Exception as e:
            proj_checks.append(("Project validation", False, str(e)[:60]))

        # Moss index
        moss_file = wl_dir / "moss.wl"
        if moss_file.exists():
            try:
                import yaml
                data = yaml.safe_load(moss_file.read_text(encoding="utf-8")) or {}
                mc = data.get("moss", {})
                status = mc.get("status", "UNKNOWN")
                count = mc.get("document_count", 0)
                moss_ready = status == "READY"
                proj_checks.append(("Moss index", moss_ready, f"{status} ({count:,} records)"))
            except Exception:
                proj_checks.append(("Moss index", False, "could not read moss.wl"))
        else:
            proj_checks.append(("Moss index", False, "not initialized"))

    _print_checks(proj_checks)
    checks.extend(proj_checks)

    # ── 5. LLM Gateway ───────────────────────────────────────────────────────
    console.print("\n[bold]LLM Gateway[/bold]")
    llm_checks = []
    try:
        from backend.workline.llm.gateway import LLMGateway
        llm_checks.append(("LLM gateway import", True, "backend.workline.llm.gateway"))
    except ImportError:
        llm_checks.append(("LLM gateway import", False, "backend not on PYTHONPATH"))

    import os
    bedrock_key = bool(os.environ.get("AWS_ACCESS_KEY_ID"))
    nvidia_key = bool(os.environ.get("NVIDIA_API_KEY"))
    llm_checks.append(("AWS Bedrock (primary)", bedrock_key, "AWS_ACCESS_KEY_ID set" if bedrock_key else "not configured (will use LocalMock)"))
    llm_checks.append(("NVIDIA NIM (fallback)", nvidia_key, "NVIDIA_API_KEY set" if nvidia_key else "not configured (will use LocalMock)"))
    llm_checks.append(("LocalMock (offline)", True, "always available"))
    _print_checks(llm_checks)
    checks.extend(llm_checks)

    # ── 6. LiveKit ───────────────────────────────────────────────────────────
    console.print("\n[bold]LiveKit[/bold]")
    lk_checks = []
    lk_url = os.environ.get("LIVEKIT_URL", "")
    lk_key = bool(os.environ.get("LIVEKIT_API_KEY"))
    lk_checks.append(("LIVEKIT_URL set", bool(lk_url), lk_url or "not set (realtime sessions require URL)"))
    lk_checks.append(("LIVEKIT_API_KEY set", lk_key, "set" if lk_key else "not set (local token fallback active)"))
    _print_checks(lk_checks)
    checks.extend(lk_checks)

    # ── 7. Git ───────────────────────────────────────────────────────────────
    console.print("\n[bold]Git[/bold]")
    git_checks = []
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=3)
        git_ok = result.returncode == 0
        git_checks.append(("git available", git_ok, result.stdout.strip() if git_ok else "not found"))
    except FileNotFoundError:
        git_checks.append(("git available", False, "git not found in PATH"))
    _print_checks(git_checks)
    checks.extend(git_checks)

    # ── Summary ──────────────────────────────────────────────────────────────
    total = len(checks)
    passed = sum(1 for _, ok, _ in checks if ok)
    failed = total - passed

    console.print()
    if failed == 0:
        console.print(f"[bold green]All {total} checks passed.[/bold green]\n")
    else:
        console.print(f"[bold]{passed}/{total} checks passed — [red]{failed} issues[/red] detected.\n[/bold]")
        console.print("[dim]Tip: Run [bold]wg start[/bold] to start the WORKLINE stack if services are down.[/dim]\n")


def _print_checks(checks: list) -> None:
    for label, ok, detail in checks:
        icon = _mark(ok)
        detail_str = f"[dim]{detail}[/dim]" if detail else ""
        console.print(f"  {icon} {label}  {detail_str}")


def _find_compose_file() -> Optional[Path]:
    candidates = ["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]
    current = Path.cwd().resolve()
    for _ in range(8):
        for name in candidates:
            f = current / name
            if f.exists():
                return f
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None
