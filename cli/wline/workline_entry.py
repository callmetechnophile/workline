"""
Main entry point for `workline` command.
Primary bootstrap entrypoint is:
    workline --activate
"""

import os
from pathlib import Path
import sys

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cli.wline.core.activator import main as activator_main


def main() -> None:
    """Executable entry point for workline."""
    activator_main()


if __name__ == "__main__":
    main()
