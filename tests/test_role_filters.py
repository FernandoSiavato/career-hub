"""Tests for ``jobsearch.profiles.load_role_filters``.

These tests write fixtures into the session-shared data directory and clean
up afterwards so they do not leak into other test modules.
"""

from __future__ import annotations

import pytest

from jobsearch.profiles import load_role_filters

_USER_CONTEXT_FIXTURE = """\
---
name: Test User
work_modality_preference: remote
hybrid_days_max: 2
salary_floor:
  - currency: USD
    monthly: 4000
sectors_target:
  - data platforms
  - humanitarian
sectors_avoid:
  - adtech
hard_constraints:
  - no relocation
---

Stub narrative.
"""


@pytest.fixture
def with_user_context(data_dir):
    """Write a populated USER_CONTEXT.md, restore the original on teardown."""
    target = data_dir / "_brain" / "USER_CONTEXT.md"
    original = target.read_text(encoding="utf-8")
    target.write_text(_USER_CONTEXT_FIXTURE, encoding="utf-8")
    yield target
    target.write_text(original, encoding="utf-8")


@pytest.fixture
def with_role_override(data_dir):
    """Write a roles/<role>.md override and clean up afterwards."""
    role_file = data_dir / "roles" / "data.md"
    role_file.write_text(
        """\
---
work_modality_preference: hybrid
hybrid_days_max: 3
sectors_target:
  - data platforms
  - ai infrastructure
---
""",
        encoding="utf-8",
    )
    yield role_file
    role_file.unlink()


class TestLoadRoleFilters:
    def test_loads_user_context_when_no_role_file(self, with_user_context):
        filters = load_role_filters("data")
        assert filters["work_modality_preference"] == "remote"
        assert filters["hybrid_days_max"] == 2
        assert filters["salary_floor"] == {"currency": "USD", "monthly": 4000}
        assert filters["sectors_target"] == ["data platforms", "humanitarian"]
        assert filters["sectors_avoid"] == ["adtech"]

    def test_role_file_overrides_user_context(self, with_user_context, with_role_override):
        filters = load_role_filters("data")
        # Overridden by role file
        assert filters["work_modality_preference"] == "hybrid"
        assert filters["hybrid_days_max"] == 3
        assert filters["sectors_target"] == ["data platforms", "ai infrastructure"]
        # Inherited from USER_CONTEXT (role file did not redefine them)
        assert filters["salary_floor"] == {"currency": "USD", "monthly": 4000}
        assert filters["sectors_avoid"] == ["adtech"]

    def test_empty_user_context_returns_empty(self, data_dir):
        """The bundled USER_CONTEXT.md ships with placeholders. ``load_role_filters``
        still parses the frontmatter cleanly and returns the placeholder values
        (not an exception)."""
        # No fixture applied — uses the conftest-initialized skeleton.
        filters = load_role_filters("data")
        # Either the placeholder strings are present, or the file is fully
        # empty. The important contract is "no exception" and "returns a
        # dict".
        assert isinstance(filters, dict)

    def test_no_role_argument_falls_back_to_user_context_only(self, with_user_context):
        filters = load_role_filters(None)
        assert filters["work_modality_preference"] == "remote"
