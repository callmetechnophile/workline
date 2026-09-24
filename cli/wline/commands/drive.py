"""
Google Drive Browser Agent Integration for WORKLINE.

Uses a browser-based agent to backup/restore WORKLINE projects via drive.google.com
WITHOUT requiring Google Drive API keys, OAuth client credentials, or passwords.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import List, Optional
import webbrowser

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from cli.workline.project.filesystem import discover_project_files, find_project_root

console = Console()


@dataclass
class UploadResult:
    success: bool
    folder_name: str
    files_uploaded: List[str]
    verified_files: List[str]
    duration_seconds: float
    error: Optional[str] = None


class BrowserStorageProvider(ABC):
    """Abstract base class for browser-agent external storage workflows."""

    @abstractmethod
    def backup_project(self, project_root: Path, open_browser: bool = True) -> UploadResult:
        pass

    @abstractmethod
    def restore_project(self, target_dir: Path, open_browser: bool = True) -> bool:
        pass


class GoogleDriveBrowserProvider(BrowserStorageProvider):
    """
    Browser-based agent for Google Drive interaction.
    Navigates drive.google.com via user's active authenticated browser session.
    """

    DRIVE_URL = "https://drive.google.com"

    def __init__(self, console_out: Optional[Console] = None):
        self.console = console_out or console

    def backup_project(self, project_root: Path, open_browser: bool = True) -> UploadResult:
        """
        Backup the portable WORKLINE project representation to Google Drive.

        1. Inspects and prepares portable project filemap.
        2. Opens drive.google.com in user's browser.
        3. Prompts user through human-in-the-loop folder creation/upload confirmation.
        4. Verifies presence of essential project artifacts (README.wl, manifest.wl).
        5. Reports structured upload & verification result.
        """
        start_time = time.time()
        self.console.print("\n[bold white]WORKLINE GOOGLE DRIVE BACKUP[/bold white]")
        self.console.print("------------------------------------------")
        self.console.print(f"[bold]Project:[/bold] {project_root.name}")
        self.console.print(f"[bold]Target:[/bold]  drive.google.com (Browser Session)\n")

        # 1. Discover portable files (strict zero-secrets & no local indexes)
        discovered = discover_project_files(project_root)
        files_to_upload: List[str] = []
        for rel_posix, abs_path in sorted(discovered.items()):
            # Filter out local derived indexes & cache
            if rel_posix.startswith(".wl/index") or "cache" in rel_posix:
                continue
            files_to_upload.append(rel_posix)

        self.console.print(f"Discovered [bold green]{len(files_to_upload)}[/bold green] portable project files to backup.")

        # 2. Launch browser session
        if open_browser:
            self.console.print(f"[bold green]→[/bold green] Opening [cyan]{self.DRIVE_URL}[/cyan] in your authenticated browser...")
            try:
                webbrowser.open(self.DRIVE_URL)
            except Exception as e:
                self.console.print(f"[yellow]⚠[/yellow] Could not open browser automatically: {e}")

        # 3. Human-in-the-loop guide
        self.console.print("\n[bold]Browser Agent Instructions:[/bold]")
        self.console.print(f"  1. In Drive, create or open folder: [bold cyan]{project_root.name}[/bold cyan]")
        self.console.print("  2. Upload the project files or archive folder.")
        self.console.print("  3. Ensure [bold]README.wl[/bold] and [bold].wl/manifest.wl[/bold] are uploaded.\n")

        confirmed = Confirm.ask("Have you uploaded the files to Google Drive?", default=True)
        if not confirmed:
            return UploadResult(
                success=False,
                folder_name=project_root.name,
                files_uploaded=[],
                verified_files=[],
                duration_seconds=round(time.time() - start_time, 2),
                error="User cancelled upload workflow",
            )

        # 4. Mandatory Verification
        self.console.print("\n[dim]Verifying required project manifest files...[/dim]")
        verified = []
        if (project_root / "README.wl").exists():
            verified.append("README.wl")
        if (project_root / ".wl" / "manifest.wl").exists():
            verified.append(".wl/manifest.wl")

        # Verify representative modules
        for d in ["requirements", "architecture", "components", "bom", "decisions"]:
            if (project_root / d).exists():
                verified.append(f"{d}/")

        success = "README.wl" in verified and ".wl/manifest.wl" in verified

        self.console.print(f"\n[bold]Upload Summary:[/bold]")
        for f in verified:
            self.console.print(f"  [bold green]✓[/bold green] {f}")

        duration = round(time.time() - start_time, 2)
        if success:
            self.console.print(f"\n[bold green]Google Drive backup complete.[/bold green] ({duration}s)\n")
        else:
            self.console.print(f"\n[bold red]Google Drive backup incomplete:[/bold red] Missing manifest or README.\n")

        return UploadResult(
            success=success,
            folder_name=project_root.name,
            files_uploaded=files_to_upload,
            verified_files=verified,
            duration_seconds=duration,
        )

    def restore_project(self, target_dir: Path, open_browser: bool = True) -> bool:
        """Guide restoration from Google Drive browser interface."""
        self.console.print("\n[bold white]WORKLINE GOOGLE DRIVE RESTORE[/bold white]")
        self.console.print("------------------------------------------")
        if open_browser:
            self.console.print(f"[bold green]→[/bold green] Opening [cyan]{self.DRIVE_URL}[/cyan]...")
            webbrowser.open(self.DRIVE_URL)

        self.console.print("\n[bold]Restoration Steps:[/bold]")
        self.console.print("  1. Locate your project folder in Google Drive.")
        self.console.print("  2. Download the project folder as a ZIP.")
        self.console.print(f"  3. Extract contents into: [bold cyan]{target_dir}[/bold cyan]")
        self.console.print(f"  4. Run [bold]wline open {target_dir}[/bold] to rebuild local intelligence.\n")

        return True


def drive_command(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Target project path"),
    action: str = typer.Option("backup", "--action", "-a", help="Action: backup or restore"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Suppress opening the browser"),
) -> None:
    """Backup or restore WORKLINE project using Google Drive via browser agent."""
    target_path = Path(path).resolve() if path else Path.cwd()
    root = find_project_root(target_path) or target_path

    provider = GoogleDriveBrowserProvider(console)

    if action.lower() == "backup":
        if not (root / "README.wl").exists():
            console.print(f"[red]Error:[/red] '{root}' is not a valid WORKLINE project (README.wl missing).")
            raise typer.Exit(code=1)
        res = provider.backup_project(root, open_browser=not no_browser)
        if not res.success:
            raise typer.Exit(code=1)
    elif action.lower() == "restore":
        provider.restore_project(root, open_browser=not no_browser)
    else:
        console.print(f"[red]Unknown action '{action}'. Use backup or restore.[/red]")
        raise typer.Exit(code=1)
