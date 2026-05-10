"""Test setup: provision a temporary career-hub data directory before any
jobsearch import so ``ROOT``, ``DB_PATH`` and ``PROFILES_DIR`` resolve there.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest

# Resolved BEFORE pytest imports any test module — therefore before any
# ``from jobsearch import ...`` runs. This ensures the package globals point at
# a clean, disposable directory rather than the developer's real ~/.career-hub.
_TEST_DIR = Path(tempfile.mkdtemp(prefix="career-hub-test-"))
os.environ["JOBSEARCH_DATA_DIR"] = str(_TEST_DIR)


def pytest_sessionfinish(session, exitstatus):  # noqa: ARG001
    shutil.rmtree(_TEST_DIR, ignore_errors=True)


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Path to the session-wide career-hub data directory used by tests."""
    return _TEST_DIR


@pytest.fixture(scope="session", autouse=True)
def _initialized_data_dir(data_dir: Path) -> Path:
    """Run ``run_init`` once per test session to populate the test data dir
    with the standard folder layout, templates and SQLite tracker."""
    from jobsearch.init_cmd import run_init

    run_init(data_dir)
    return data_dir


@pytest.fixture
def fresh_db(tmp_path: Path) -> Path:
    """Per-test isolated SQLite database initialized with the schema."""
    from jobsearch.database import init_db

    db_path = tmp_path / "test.db"
    init_db(db_path=db_path)
    return db_path


@pytest.fixture
def sample_profile() -> dict:
    """Minimal profile dict matching the structure produced by load_profile."""
    return {
        "role_key": "data",
        "name": "Test User",
        "city": "Remote",
        "role_title": "Data Analyst",
        "positioning": "Data analyst with three years of experience.",
        "total_years_experience": 3,
        "achievements": ["Built an ETL pipeline that reduced manual reporting by 40%."],
        "skills": [
            {"name": "Python", "level": 4, "aliases": ["python3"]},
            {"name": "SQL", "level": 4, "aliases": ["postgresql", "mysql"]},
            {"name": "Power BI", "level": 3, "aliases": ["powerbi", "power-bi"]},
            {"name": "Excel", "level": 4, "aliases": []},
        ],
    }


@pytest.fixture
def sample_jd_text() -> str:
    """Synthetic JD text with a mix of required and optional skills."""
    return """
    Data Analyst — Acme Corp

    Requerimos un analista con experiencia de 2 años en Python y SQL.
    Conocimiento en Power BI es indispensable. Excel avanzado requerido.
    Conocimientos en Tableau es deseable.
    Se valora experiencia con dbt.
    """
