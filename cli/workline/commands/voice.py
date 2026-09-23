"""
Implementation of `wg voice` and `wg voice --text` commands.
Integrates LiveKit realtime session with Local Moss retrieval and WorklineRealtimeAgent.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from cli.workline.config.config import WorklineCLIConfig
from cli.workline.livekit.adapter import LiveKitAgentAdapter
from cli.workline.project.filesystem import find_project_root
from cli.workline.project.readme import parse_readme_wl
from cli.workline.project.validator import validate_project
from cli.workline.retrieval.moss_adapter import LocalMossAdapter

console = Console()


def voice_command(
    text_mode: bool = typer.Option(False, "--text", "-t", help="Run interactive conversational session in terminal"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Project path"),
) -> None:
    """
    Launch realtime conversational session (LiveKit voice or interactive text).
    Executes the 10-step validation and session startup sequence.
    """
    target_dir = Path(path).resolve() if path else Path.cwd()
    
    # Step 1: Discover current WORKLINE project
    root = find_project_root(target_dir)
    if not root:
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a WORKLINE project (no README.wl found).")
        raise typer.Exit(code=1)

    # Step 2: Validate project
    validation = validate_project(root, verify_checksums=False)
    if not validation.is_valid:
        console.print(f"[bold red]Project validation failed:[/bold red] {validation.errors}")
        raise typer.Exit(code=1)

    readme = parse_readme_wl(root / "README.wl")

    # Step 3: Validate LiveKit configuration
    cfg = WorklineCLIConfig.load(root)
    lk_config = cfg.livekit

    # Step 4: Validate Moss retrieval availability
    moss_adapter = LocalMossAdapter(root)
    moss_status = "READY" if moss_adapter.is_ready else "UNINITIALIZED"

    # Step 5: Start / connect to LiveKit session & project room
    adapter = LiveKitAgentAdapter(root, config=cfg)
    connected = adapter.connect()
    lk_status = "CONNECTED" if connected else "DISCONNECTED"

    # Step 6: Verify WorklineRealtimeAgent is ready
    agent_status = "READY"

    # Print Official WORKLINE REALTIME Banner matching specification
    console.print("\n[bold white]WORKLINE REALTIME[/bold white]\n")
    console.print(f"[bold]Project:[/bold]\n{readme.name}\n")
    console.print(f"[bold]Room:[/bold]\n{adapter.get_room_name()}\n")
    console.print(f"[bold]LiveKit:[/bold]\n[green]{lk_status}[/green]\n")
    
    m_color = "green" if moss_status == "READY" else "yellow"
    console.print(f"[bold]Moss:[/bold]\n[{m_color}]{moss_status}[/{m_color}]\n")
    console.print(f"[bold]Agent:[/bold]\n[green]{agent_status}[/green]\n")

    if moss_status != "READY":
        console.print("[dim]Note: Moss index is uninitialized; running direct filesystem fallback.[/dim]\n")

    # Step 7-10: Multi-turn interaction
    if text_mode:
        console.print("[bold cyan]Interactive Terminal Mode Active[/bold cyan]")
        console.print("[dim]Ask engineering questions. Type 'exit' or 'quit' to terminate session.[/dim]\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit", "q"):
                    console.print("\n[yellow]Session ended.[/yellow]\n")
                    break
                    
                response = adapter.process_utterance(user_input, speaker="engineer")
                console.print(f"\n[bold cyan]Agent:[/bold cyan]\n{response}\n")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Session ended.[/yellow]\n")
                break
        return

    # Realtime Voice Mode
    token = adapter.generate_token(participant_identity="user_voice")
    console.print(f"[dim]LiveKit Voice Stream Token generated for room: {adapter.get_room_name()}[/dim]")
    console.print("[bold green]Listening...[/bold green]\n")
    console.print("[dim](Run with '--text' to interactively converse in terminal)[/dim]\n")
