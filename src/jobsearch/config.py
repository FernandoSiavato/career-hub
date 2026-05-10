"""Runtime configuration loaded from ``$JOBSEARCH_DATA_DIR/config.toml``.

The TOML file declares the user's roles (e.g. ``data``, ``meal``, ``product``) and
maps each role to a CV template, an output folder, and a numeric sector id used
for legacy code paths. If no config file is present, a minimal fallback with two
example roles (``data``, ``product``) is used so that ``--help`` and tests can run
without any user setup.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from jobsearch import ROOT

if sys.version_info >= (3, 11):
    import tomllib  # type: ignore[import-not-found]
else:  # pragma: no cover - 3.10 fallback
    import tomli as tomllib  # type: ignore[import-not-found]

PORTALS_PATH = ROOT / "portals.yml"
CONFIG_PATH = ROOT / "config.toml"
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")

JD_FILENAMES = [
    "JOB.docx",
    "Job.docx",
    "job.docx",
    "JD.docx",
    "JD.pdf",
    "Job.pdf",
    "JOB.pdf",
    "description.docx",
    "description.pdf",
    "descripcion.docx",
    "descripcion.pdf",
]

FIT_THRESHOLD = 0.70
SKILL_WEIGHTS = {"skills": 0.7, "experience": 0.3}


# ---------------------------------------------------------------------------
# Fallback config used when no config.toml exists.
# Keeps the CLI importable on a fresh machine before the user runs ``init``.
# ---------------------------------------------------------------------------

_FALLBACK_CONFIG: dict = {
    "default_role": "data",
    "roles": {
        "data": {
            "sector": 1,
            "profile": "PROFILE_DATA",
            "folder": "applications/data",
            "cv_templates": {"es": "cvs/CV_DATA.docx", "en": "cvs/CV_DATA.docx"},
        },
        "product": {
            "sector": 2,
            "profile": "PROFILE_PRODUCT",
            "folder": "applications/product",
            "cv_templates": {"es": "cvs/CV_PRODUCT.docx", "en": "cvs/CV_PRODUCT.docx"},
        },
    },
}


def _load_raw_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return _FALLBACK_CONFIG
    return _FALLBACK_CONFIG


_CONFIG = _load_raw_config()


def available_roles() -> list[str]:
    """Return the list of role keys defined in the active config."""
    return list(_CONFIG.get("roles", {}).keys())


def default_role() -> str:
    roles = available_roles()
    fallback = _CONFIG.get("default_role")
    if fallback and fallback in roles:
        return fallback
    return roles[0] if roles else "data"


def role_config(role: str) -> dict:
    return _CONFIG.get("roles", {}).get(role, {})


def cv_template_path(role: str, lang: str) -> Path:
    rc = role_config(role)
    rel = (rc.get("cv_templates") or {}).get(lang)
    if not rel:
        templates = rc.get("cv_templates") or {}
        if templates:
            rel = next(iter(templates.values()))
    if not rel:
        raise FileNotFoundError(
            f"No CV template configured for role={role!r} lang={lang!r} in config.toml"
        )
    return ROOT / rel


# ---------------------------------------------------------------------------
# Backward-compatible exports — these dicts are read elsewhere in the codebase.
# They are computed from the loaded TOML so existing call sites keep working
# without knowing whether the data is hardcoded or user-provided.
# ---------------------------------------------------------------------------

ROLE_SECTOR: dict[str, int] = {
    role: int(cfg.get("sector", idx + 1))
    for idx, (role, cfg) in enumerate(_CONFIG.get("roles", {}).items())
}

SECTOR_FOLDER: dict[int, str] = {
    int(cfg.get("sector", idx + 1)): str(cfg.get("folder", f"applications/{role}"))
    for idx, (role, cfg) in enumerate(_CONFIG.get("roles", {}).items())
}

ROLE_PROFILE: dict[str, str] = {
    role: str(cfg.get("profile", f"PROFILE_{role.upper()}"))
    for role, cfg in _CONFIG.get("roles", {}).items()
}

CV_TEMPLATES: dict[str, dict[str, Path]] = {
    role: {lang: ROOT / rel for lang, rel in (cfg.get("cv_templates") or {}).items()}
    for role, cfg in _CONFIG.get("roles", {}).items()
}
