# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-05-11

First successful PyPI release. ``v0.1.0`` was tagged twice and both
attempts were rejected by PyPI; ``v0.1.1`` is the version that actually
ships.

### Fixed
- ``pyproject.toml``: removed a ``[tool.hatch.build.targets.wheel.force-include]``
  block that re-packed ``src/jobsearch/templates`` on top of the regular
  ``packages = ["src/jobsearch"]`` sweep. The duplicate entries produced
  a wheel that PyPI rejected with ``HTTP 400 — Invalid distribution file``.

## [Unreleased]

### Added
- Initial repository scaffold extracted from a private monorepo.
- MIT license, .gitignore, .env.example, README skeleton, credits.
- Vendored copy of the `jobsearch` Python CLI (11 modules) and the `/apply` Claude Code skill.
- `pyproject.toml` (PEP 621, hatchling) with optional extras `scan`, `web`, `dev`.
- `career-hub init` command that provisions a data directory with the standard folder layout,
  copies bundled templates (including 8 per-folder `CLAUDE.md` guides), and initializes the
  SQLite tracker.
- 9 per-folder `CLAUDE.md` guides explaining each part of a career-hub data directory.
- Deep docs: `docs/ARCHITECTURE.md`, `docs/SKILL_APPLY.md`, `docs/SCANNER.md`.
- `CONTRIBUTING.md` with the contributor workflow.
- pytest suite (55 tests across 5 files) covering profiles, fit analyzer, database,
  init_cmd, and cover letter generation. Coverage gate: 60% (currently 67%).
- GitHub Actions `ci.yml` (ruff check, ruff format check, pytest on Python 3.10-3.12 across
  ubuntu and windows) and `release.yml` (PyPI trusted publishing on `v*` tags).
- Issue templates for bug reports and feature requests.
- README badges: CI, PyPI, Python versions, license, downloads.

### Changed
- Code paths and personal identifiers abstracted out of `cover_letter.py` and `cv_builder.py`:
  generic fallbacks (``Your Name`` and `CV_{role}_{company}_{date}.docx`) replace the
  hardcoded author values; city is now read from the profile rather than hardcoded.
- Roles, sectors, and CV template paths are now driven by `config.toml` rather than hardcoded
  Python dictionaries.

### Fixed
- `init_cmd._copy_template` now walks `importlib.resources` paths one segment at a time so
  per-folder template files are copied correctly with editable installs and multi-root
  resource layouts.
- `fit_analyzer.YEARS_PATTERNS` accept the normalized form (`anos`) instead of `años`, so
  Spanish JDs that mention experience requirements no longer return zero years.

### Notes
- `v0.1.0` is targeted at the end of Phase 5 once the PyPI trusted publisher is configured.
  Local install via `pip install -e .` already works.
