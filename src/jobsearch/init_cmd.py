"""Implementation of ``career-hub init``.

Creates a fresh career-hub data directory with the standard folder layout,
copies the bundled templates (``config.toml``, starter profiles, ``CLAUDE.md``,
``START_HERE.md``, ``portals.yml``, ``.gitignore``), and initializes the SQLite
tracker. Idempotent: running it twice on the same directory does not overwrite
existing files.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

# Folders created at the root of every new career-hub data directory.
# Each maps to its purpose in CLAUDE.md.
DATA_DIR_FOLDERS: list[str] = [
    "profiles",
    "cvs",
    "cvs/scripts",
    "roles",
    "work_experience",
    "documentation_hub",
    "certificates",
    "personal_brand",
    "applications",
]

# (template-relative-path, destination-relative-path)
TEMPLATE_FILES: list[tuple[str, str]] = [
    ("config.toml", "config.toml"),
    ("portals.yml", "portals.yml"),
    (".gitignore", ".gitignore"),
    (".env.example", ".env.example"),
    ("CLAUDE.md", "CLAUDE.md"),
    ("START_HERE.md", "START_HERE.md"),
    ("profiles/PROFILE_DATA.md", "profiles/PROFILE_DATA.md"),
    ("profiles/PROFILE_PRODUCT.md", "profiles/PROFILE_PRODUCT.md"),
    # Per-folder CLAUDE.md guides — these tell any AI agent that opens the
    # folder how to help the user populate or work with it.
    ("profiles/CLAUDE.md", "profiles/CLAUDE.md"),
    ("cvs/CLAUDE.md", "cvs/CLAUDE.md"),
    ("roles/CLAUDE.md", "roles/CLAUDE.md"),
    ("work_experience/CLAUDE.md", "work_experience/CLAUDE.md"),
    ("documentation_hub/CLAUDE.md", "documentation_hub/CLAUDE.md"),
    ("certificates/CLAUDE.md", "certificates/CLAUDE.md"),
    ("personal_brand/CLAUDE.md", "personal_brand/CLAUDE.md"),
    ("applications/CLAUDE.md", "applications/CLAUDE.md"),
]


def _copy_template(template_rel: str, dest: Path, force: bool = False) -> bool:
    """Copy a packaged template file to ``dest``. Returns True if written."""
    if dest.exists() and not force:
        return False
    pkg_root = resources.files("jobsearch.templates")
    # ``MultiplexedPath.joinpath`` accepts only a single positional argument,
    # so build the resource path one segment at a time. This keeps the code
    # working regardless of whether ``pkg_root`` is a real ``Path`` or a
    # multiplexed importlib.resources path (which happens with editable
    # installs that span multiple template roots).
    src = pkg_root
    for part in template_rel.split("/"):
        src = src.joinpath(part)
    content = src.read_text(encoding="utf-8")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return True


def run_init(data_dir: Path, force: bool = False) -> dict:
    """Initialize a career-hub data directory at ``data_dir``.

    Returns a summary dict with the lists of folders created, files written,
    and files skipped (already present). The caller is responsible for any
    user-facing rendering.
    """
    data_dir = Path(data_dir).expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    folders_created: list[str] = []
    for rel in DATA_DIR_FOLDERS:
        target = data_dir / rel
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            folders_created.append(rel)
            # Drop a .keep so empty folders survive ``git add``.
            (target / ".keep").write_text("", encoding="utf-8")

    files_written: list[str] = []
    files_skipped: list[str] = []
    for tmpl_rel, dest_rel in TEMPLATE_FILES:
        dest = data_dir / dest_rel
        if _copy_template(tmpl_rel, dest, force=force):
            files_written.append(dest_rel)
        else:
            files_skipped.append(dest_rel)

    # Initialize the SQLite tracker against the freshly-created directory.
    # ``init_db`` accepts an explicit path so we do not have to reload the
    # package globals just because the user picked a non-default data dir.
    from jobsearch.database import init_db

    init_db(db_path=data_dir / "jobsearch.db")

    return {
        "data_dir": str(data_dir),
        "folders_created": folders_created,
        "files_written": files_written,
        "files_skipped": files_skipped,
    }
