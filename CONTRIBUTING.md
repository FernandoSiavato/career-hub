# Contributing

career-hub is open source under the MIT license. PRs are welcome once we
hit `v0.1.0` on PyPI (currently in alpha, mid-extraction from a private
monorepo). Until then, please open issues to discuss before submitting
patches; the codebase is moving fast.

## Quick setup

```bash
git clone https://github.com/fernandosiavato/career-hub.git
cd career-hub
python -m venv .venv
. .venv/bin/activate           # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev,all]"
```

Run the CLI without installing globally:

```bash
PYTHONPATH=src python -m jobsearch --help
```

Run against a throwaway data directory:

```bash
JOBSEARCH_DATA_DIR=/tmp/career-hub-dev python -m jobsearch init
JOBSEARCH_DATA_DIR=/tmp/career-hub-dev python -m jobsearch report
```

## Style

- **Lint:** `ruff check .`
- **Format:** `ruff format .`
- **Line length:** 100.
- **Imports:** stdlib → third-party → first-party, separated by blank lines.
- **Type hints:** required on public functions, optional on internals.
- **Docstrings:** one short line for any function or module a contributor
  might land on. Skip it for trivial private helpers.

## Tests

(Phase 5 — coming. Once the suite exists:)

```bash
pytest
pytest --cov=jobsearch --cov-report=term-missing
```

Target: 60% coverage minimum on `profiles.py`, `fit_analyzer.py`,
`config.py`, `init_cmd.py`, `database.py`. UI / skill tests live in
the `tests/skills/` subfolder.

## Project structure

See [CLAUDE.md](CLAUDE.md) for the contributor-facing repo guide and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the design doc.

## Commit messages

We use Conventional Commits:

```
feat(init): add per-folder CLAUDE.md to template payload
fix(scanner): handle Workday tenants without a public site
docs(readme): clarify what JOBSEARCH_DATA_DIR controls
chore(deps): bump rich to 13.7
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`.

Keep commits small and focused. One logical change per commit.

## Pull request checklist

- [ ] Branch off `main`, branch name `feat/<short-slug>` or `fix/<short-slug>`.
- [ ] `ruff check .` passes.
- [ ] `pytest` passes (when the suite exists).
- [ ] If you added a new template file, you also added it to
      `init_cmd.py:TEMPLATE_FILES` and verified `career-hub init` deploys it.
- [ ] If you changed CLI behavior, the README and `docs/` reflect it.
- [ ] If you changed the `/apply` skill, you updated `docs/SKILL_APPLY.md`.
- [ ] Conventional Commit message.

## Things we will not merge

- Auto-submission of applications. This is a deliberate design boundary.
  See [docs/SKILL_APPLY.md](docs/SKILL_APPLY.md) for the rationale.
- Telemetry. career-hub does not phone home.
- Cloud sync that sends user data outside the user's machine without an
  explicit, file-by-file opt in.

## Reporting security issues

Email <fernando@siavato.com> with the subject "career-hub security".
Do not open public issues for vulnerabilities. We will respond within 7
days.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
By participating, you agree to its terms.

## A small ask

If career-hub is useful to you, the lowest-effort way to support the
project is to [follow @fernandosiavato](https://github.com/fernandosiavato)
on GitHub and star the repository. That signal helps when we decide
where to spend time.
