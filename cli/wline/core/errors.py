"""
Deterministic exit codes and exception handling for the WORKLINE CLI.

Exit codes:
  0 = Success
  1 = General error
  2 = Invalid command/arguments
  3 = Configuration error
  4 = Authorization failure
  5 = Service unavailable
  6 = Task failure
  7 = Timeout
  8 = Cancellation
  9 = Validation failure
"""

from enum import IntEnum
import json
import sys
from typing import Any, Optional
import typer
from rich.console import Console

console = Console()
err_console = Console(stderr=True)


class ExitCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_ARGUMENTS = 2
    CONFIG_ERROR = 3
    AUTH_FAILURE = 4
    SERVICE_UNAVAILABLE = 5
    TASK_FAILURE = 6
    TIMEOUT = 7
    CANCELLATION = 8
    VALIDATION_FAILURE = 9


def exit_with_error(
    message: str,
    code: ExitCode = ExitCode.GENERAL_ERROR,
    details: Optional[str] = None,
    json_mode: bool = False,
) -> None:
    """Exit the CLI cleanly with a deterministic exit code, supporting --json."""
    if json_mode:
        payload = {
            "status": "error",
            "code": int(code),
            "error": message,
        }
        if details:
            payload["details"] = details
        # Output clean JSON to stdout or stderr
        print(json.dumps(payload, indent=2))
    else:
        err_console.print(f"[bold red]Error:[/] {message}")
        if details:
            err_console.print(f"[dim]{details}[/dim]")
    raise typer.Exit(code=int(code))


def print_json_output(data: Any) -> None:
    """Print purely clean JSON to stdout without banners or ANSI codes."""
    print(json.dumps(data, indent=2, default=str))
