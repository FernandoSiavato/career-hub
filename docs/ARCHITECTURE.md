# Architecture

career-hub is a small Python package plus a Claude Code skill plus a
folder-template system. The whole thing is local-first: everything reads
and writes inside `$JOBSEARCH_DATA_DIR`, and there is no server.

## High-level data flow

```
                  +-----------------------------+
                  |  User's data directory      |
                  |  ($JOBSEARCH_DATA_DIR)      |
                  |                             |
                  |   profiles/                 |
                  |   cvs/                      |
                  |   work_experience/          |
                  |   documentation_hub/        |
                  |   certificates/             |
                  |   personal_brand/           |
                  |   applications/             |
                  |   jobsearch.db              |
                  |   config.toml               |
                  |   portals.yml               |
                  +--+--------+-------+---------+
                     ^        ^       ^
                     |        |       |
        +------------+        |       +--------------+
        |                     |                      |
   +----+-----+        +------+------+        +------+------+
   |   CLI    |        |  /apply     |        |  Scanner    |
   | jobsearch|        |  skill      |        |  scanner.py |
   |__main__  |        |(.claude/    |        |  scanner_   |
   |          |        | skills/     |        |  apify.py   |
   |          |        | apply)      |        |             |
   +----+-----+        +-------------+        +------+------+
        |                                            |
        v                                            v
  +-----+-----+                              +-------+-----+
  | SQLite    |  <---  jobs land here        | Greenhouse  |
  | tracker   |                              | Ashby       |
  | (apps,    |                              | Lever       |
  |  scanned_ |                              | Workday     |
  |  jobs)    |                              | Apify (opt) |
  +-----------+                              +-------------+
```

## Modules

### Package root: `src/jobsearch/__init__.py`

Resolves `ROOT` from `JOBSEARCH_DATA_DIR` (or `~/.career-hub`). Everything
else in the package imports `ROOT`, `DB_PATH`, `PROFILES_DIR` from here.

### Configuration: `config.py`

Loads `config.toml` from the data directory. Exposes:

- `available_roles()` / `default_role()` — for the CLI `Choice`.
- `role_config(role)` — raw dict for one role.
- `cv_template_path(role, lang)` — resolves to an absolute Path.
- Backward-compatible exports `ROLE_SECTOR`, `SECTOR_FOLDER`,
  `ROLE_PROFILE`, `CV_TEMPLATES` are computed from the TOML so older
  call sites keep working.

If `config.toml` is missing, a fallback dict with two example roles
(`data`, `product`) keeps `--help` working on a fresh machine.

### CLI: `__main__.py`

A click group with one command per workflow step:

| Command | Purpose |
|---------|---------|
| `init` | Create a fresh data directory with templates and SQLite. |
| `fit` | Score a JD against a profile, write `fit_report.md`. |
| `upword` | Generate a humanized cover letter for a JD. |
| `apply` | One-shot: create folder, copy CV, score fit, generate letter. |
| `log` | Update an application's status. |
| `new` | Create an empty folder for a company. |
| `report` | Dashboard of applications and skill gap patterns. |
| `scan` | Discover new openings via ATS APIs and Apify. |
| `scanned` | List jobs the scanner found. |
| `scanned-mark` | Promote / reject / archive a scanned job. |
| `fit-scanned` | Run fit analysis on scanned jobs in batch. |
| `enrich-workday` | Backfill JD descriptions for Workday postings. |
| `web` | Launch the optional Flask dashboard. |

The group-level callback calls `init_db()` only when `ROOT` exists, so
`career-hub init` and `career-hub --help` work on a machine that has
never been initialized.

### Profile loader: `profiles.py`

Reads YAML frontmatter from `PROFILE_*.md` files. Provides:

- `normalize(text)` — accent-strip + lowercase + whitespace collapse.
- `SKILL_DICTIONARY` — vocabulary used to detect skills in JD text.
- `fuzzy_match_skill(skill, profile_skills)` — alias + fuzzy matching
  with `difflib.SequenceMatcher` at 0.82 threshold.
- `match_skills_against_profile(jd_skills, profile)` — used by
  `fit_analyzer`.

### Fit analyzer: `fit_analyzer.py`

Reads a JD (DOCX, PDF, or plain text), extracts skills with the
dictionary in `profiles.py`, and produces a `FitReport` with:

- `skills_score` (matched required / total required), weight 0.7.
- `experience_score` (years in profile vs years required), weight 0.3.
- `fit_score` = weighted sum.
- Lists of matched skills and gaps for the report markdown.

### CV builder: `cv_builder.py`

Copies the role's CV template into the application folder under a
predictable name (`CV_<Company>_<Profile>.docx`). The actual content
tailoring happens in the `gen_cv_<company>.py` scripts written by the
`/apply` skill.

### Cover letter: `cover_letter.py`

Deterministic scaffolding (no LLM call) for a baseline cover letter
when the user runs `career-hub upword` directly. The richer, AI-generated
letters come from the `/apply` Claude Code skill, which writes prose
directly into the application folder.

### Database: `database.py`

SQLite with two main tables:

- `applications` — user's applications. `role` / `sector` are now free-form
  strings; constraints were removed in 0.1.0 to support user-defined roles.
- `scanned_jobs` — jobs found by `scanner.py` waiting to be promoted into
  applications.

`init_db(db_path=None)` accepts an explicit path so `init_cmd` can target
a freshly-created data directory without reloading package globals.

### Scanner: `scanner.py` + `scanner_apify.py`

Reads `portals.yml`, queries free ATS APIs (Greenhouse / Ashby / Lever /
Workday), filters by title keywords per profile, and dedups against
`scanned_jobs`. The Apify wrapper is optional and lazy-imports
`apify-client`.

### Web dashboard: `web.py`

Optional Flask UI for reviewing scanned jobs. Lazy-imports Flask so the
package can be used without the `[web]` extra installed.

### `/apply` skill

Lives in `.claude/skills/apply/SKILL.md`. Reads the user's
`profiles/`, `work_experience/`, `personal_brand/voice_and_tone.md`, and
`documentation_hub/`, then orchestrates the full application workflow.
Documented in detail in [SKILL_APPLY.md](SKILL_APPLY.md).

### Templates: `src/jobsearch/templates/`

Files deployed by `career-hub init`:

- Top-level: `config.toml`, `portals.yml`, `.gitignore`, `.env.example`,
  `CLAUDE.md`, `START_HERE.md`.
- Starter profiles: `PROFILE_DATA.md`, `PROFILE_PRODUCT.md`.
- Per-folder `CLAUDE.md` for `profiles/`, `cvs/`, `roles/`,
  `work_experience/`, `documentation_hub/`, `certificates/`,
  `personal_brand/`, `applications/`.

Each per-folder `CLAUDE.md` tells AI agents how to help the user populate
that specific folder.

## Why this layout

- **Source of truth = filesystem.** A user can read every file with `cat`
  or a markdown viewer. No hidden state. No "you must use the CLI".
- **AI-readable by construction.** Every important folder has a
  `CLAUDE.md`. Any AI that opens the data dir can self-orient without
  the user explaining anything.
- **Local-first.** No server, no account, no telemetry. The user
  decides whether to keep their data dir in a private git repo.
- **Optional everything.** Apify, Flask, even the scanner are optional
  extras. The minimal install runs `init`, `fit`, `apply`, `log`,
  `report` and nothing else.
