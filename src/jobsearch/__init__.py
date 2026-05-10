"""career-hub: AI-first centralized professional life database + job search CLI.

The user's career data lives in ``JOBSEARCH_DATA_DIR`` (default: ``~/.career-hub``).
That directory contains profiles, CVs, applications, work experience, certificates,
personal brand assets, and the SQLite tracking database. Everything in this package
operates relative to ``ROOT``; nothing is hardcoded to a specific machine.
"""

from __future__ import annotations

import os
from pathlib import Path

VERSION = "0.1.0"


def _resolve_root() -> Path:
    """Resolve the user's career-hub data directory.

    Order of resolution:
      1. ``JOBSEARCH_DATA_DIR`` environment variable (preferred).
      2. ``~/.career-hub`` (default for fresh installs).
    """
    env_dir = os.environ.get("JOBSEARCH_DATA_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return (Path.home() / ".career-hub").resolve()


ROOT: Path = _resolve_root()
DB_PATH: Path = ROOT / "jobsearch.db"
PROFILES_DIR: Path = ROOT / "profiles"
APPLICATIONS_DIR: Path = ROOT / "applications"
