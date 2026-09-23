"""
Commands package for WORKLINE CLI.
"""

from cli.workline.commands.init import init_project_command
from cli.workline.commands.project_ops import open_command, inspect_command, check_command
from cli.workline.commands.doctor import doctor_command
from cli.workline.commands.index import index_app
from cli.workline.commands.search import search_command
from cli.workline.commands.context import context_command
from cli.workline.commands.ask import ask_command
from cli.workline.commands.voice import voice_command
from cli.workline.commands.modules import (
    requirements_command,
    architecture_command,
    components_command,
    bom_command,
    tasks_command,
    decisions_command,
    research_command,
    documents_command,
    analysis_command,
    agents_command,
    team_command,
)
from cli.workline.commands.transfer import (
    export_command,
    import_command,
    sync_command,
    git_app,
)

__all__ = [
    "init_project_command",
    "open_command",
    "inspect_command",
    "check_command",
    "doctor_command",
    "index_app",
    "search_command",
    "context_command",
    "ask_command",
    "voice_command",
    "requirements_command",
    "architecture_command",
    "components_command",
    "bom_command",
    "tasks_command",
    "decisions_command",
    "research_command",
    "documents_command",
    "analysis_command",
    "agents_command",
    "team_command",
    "export_command",
    "import_command",
    "sync_command",
    "git_app",
]
