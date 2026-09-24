"""
WORKLINE CLI Migration Notice (`wg` is replaced by `wline`).

All WORKLINE operations now begin with:
    wline <command>

Environment activation is bootstrapped via:
    workline --activate
"""

import sys
import typer
from rich.console import Console

from cli.wline.main import app as wline_app

console = Console()

app = typer.Typer(
    name="wg",
    help="DEPRECATED: Use 'wline' instead. 'wg' is aliased to 'wline' for migration.",
    no_args_is_help=False,
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def wg_deprecation_callback(ctx: typer.Context) -> None:
    console.print(
        "[bold yellow]Notice:[/bold yellow] 'wg' has been replaced by the canonical "
        "[bold cyan]wline[/bold cyan] command. Please use [bold cyan]wline[/bold cyan].\n"
    )
    if ctx.invoked_subcommand is None:
        wline_app()


def main() -> None:
    """Invokes canonical wline app with migration notice."""
    console.print(
        "[bold yellow]Notice:[/bold yellow] 'wg' has been replaced by the canonical "
        "[bold cyan]wline[/bold cyan] command. Please use [bold cyan]wline[/bold cyan].\n"
    )
    wline_app()


if __name__ == "__main__":
    main()
