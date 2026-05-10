# Credits

## Origin and vision

`career-hub` started as a personal project by **Luis Fernando Molina** ([@fernandosiavato](https://github.com/fernandosiavato))
years ago in Notion, with a simple goal: stop rewriting his career story for every job application.

The idea grew into something bigger: a **centralized professional life database** where an AI
assistant has full access to your work history, certificates, profiles, CVs, personal brand,
and project documentation, so it can build any application, in any language, for any role,
without you having to dig through old folders.

After several iterations in Notion, the system migrated into a structured local repository
with AI-first conventions (CLAUDE.md per folder, Claude Code skills, a Python CLI for fit
analysis and document generation). This repository is the open-source extraction of that
system, generalized so anyone can run their own.

> Centralization + AI-first + your professional history as the single source of truth.

## Acknowledgments

### Scanner module — inspired by `career-ops`

The dynamic job scanner module (Greenhouse / Ashby / Lever / Apify portal scraping,
A-F evaluation matrix, modes of evaluation) is inspired by **Santi Fernandez**'s
[career-ops](https://github.com/santifer/career-ops) — a local-first AI-powered job
search system with a Go TUI dashboard. Thanks to Santi for showing what a clean
"AI proposes, human decides" workflow can look like for job hunting.

`career-hub` borrows the philosophy of the scanner (no auto-submit, human always in
control) but the rest of the system (centralized career database, /apply skill,
CLAUDE.md per folder, Python CLI for document generation) is its own design rooted
in Luis's original Notion-based vision.

### Tooling and ecosystem

- [Claude Code](https://docs.claude.com/en/docs/claude-code) — the AI coding agent that
  hosts the `/apply` skill and reads the `CLAUDE.md` files in this repo.
- [Click](https://click.palletsprojects.com/) — Python CLI framework.
- [Rich](https://rich.readthedocs.io/) — terminal output formatting.
- [python-docx](https://python-docx.readthedocs.io/) — DOCX generation for CVs.
- [pdfplumber](https://github.com/jsvine/pdfplumber) — PDF parsing for job descriptions.
- [Apify](https://apify.com/) — optional cloud actors for portals without public ATS APIs.

## Want to contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md) (added in Phase 5) for setup instructions.
For now, if `career-hub` helps you, the best contribution is to
[follow @fernandosiavato](https://github.com/fernandosiavato) and star the repo.
