# career-hub

> Your professional life, centralized. Job applications, AI-assisted.

[![CI](https://github.com/FernandoSiavato/career-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/FernandoSiavato/career-hub/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/career-hub.svg)](https://pypi.org/project/career-hub/)
[![Python versions](https://img.shields.io/pypi/pyversions/career-hub.svg)](https://pypi.org/project/career-hub/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/career-hub)](https://pepy.tech/project/career-hub)
[![Status](https://img.shields.io/badge/status-alpha-orange)](CHANGELOG.md)
[![Follow on GitHub](https://img.shields.io/github/followers/FernandoSiavato?style=social&label=Follow%20%40fernandosiavato)](https://github.com/FernandoSiavato)
[![Star this repo](https://img.shields.io/github/stars/FernandoSiavato/career-hub?style=social)](https://github.com/FernandoSiavato/career-hub)

`career-hub` is a local, AI-first **professional life database**: profiles, CVs, work
experience, certificates, project case studies, and personal brand, all structured so
any AI assistant (Claude Code, ChatGPT, your own) can read your history and build a
tailored job application in minutes instead of hours.

The system has three pieces:

1. A **Python CLI** (`jobsearch`) for fit analysis, CV generation, cover letters, and
   optional dynamic job scanning across ATS portals.
2. A **Claude Code skill** (`/apply`) that orchestrates a complete application: it reads
   the JD, picks the right profile, calculates a fit score, generates the cover letter
   and a CV-tailoring script, and only asks you for the data it cannot infer.
3. A **structured folder convention** with a `CLAUDE.md` in every folder, so any AI
   that opens the repository immediately understands what lives where, what data to
   expect, and how to help you fill it in.

> **Origin.** This project started years ago as a Notion workspace. Luis got tired of
> rewriting his career story for every job posting and migrated everything into a
> structured, AI-readable system. `career-hub` is the open-source extraction of that
> system, generalized so anyone can run their own. See [docs/CREDITS.md](docs/CREDITS.md).

---

## Status

**Alpha — not yet pip-installable.** The repo is mid-extraction from a private monorepo.
The CLI and skill currently still assume the original author's machine layout. Tracked
fixes are in [CHANGELOG.md](CHANGELOG.md). Phase 2 of the roadmap (path abstraction +
PII removal) is the next milestone before this is safe to run on a clean machine.

If you want to follow along, [follow @fernandosiavato](https://github.com/fernandosiavato)
and watch the repo. PRs and issues welcome once Phase 3 lands.

---

## The 3 levels

`career-hub` is designed to grow with you. You do not need to fill everything on day one.

### Level 1 — Setup (15 minutes)

```bash
pip install career-hub                        # not yet on PyPI (Phase 5)
career-hub init --data-dir ~/career-hub-data  # creates the folder structure
export JOBSEARCH_DATA_DIR=~/career-hub-data
```

Open the folder in Claude Code (or any AI agent that reads `CLAUDE.md`) and ask
**"explain this project and walk me through onboarding"**. The AI will read the
root `CLAUDE.md`, explain the vision, and guide you to Level 2.

**Validation:** `career-hub report` runs and shows `0 applications recorded`.

### Level 2 — First application (1-2 hours)

1. Edit `profiles/PROFILE_DEFAULT.md` with your skills, experience, and narrative.
   The AI can interview you to extract them.
2. Edit `cvs/CV_DEFAULT.docx` with your base CV (template included).
3. Find a real job posting, copy the description.
4. In Claude Code: run `/apply` and paste the JD.
5. The skill produces: `JD.md`, `keywords_gaps.md`, `cover_letter.md`, a CV-tailoring
   Python script, and a `fit_report.md`. Review, run the script, apply manually,
   then `career-hub log --company "..." --status applied`.

**Validation:** an `applications/<company>/` folder with five files, a fit score
between 0-100 you understand, and a cover letter that sounds like you.

### Level 3 — Full system (1-2 weeks)

1. Fill `work_experience/` with at least 5 past roles (STAR format + KPIs). The AI
   can interview you for these too.
2. Add your `certificates/` (PDFs + YAML metadata: issuer, date, expiry).
3. Document 3-5 case studies in `documentation_hub/` as proof of capability.
4. Configure `portals.yml` with companies you follow. `career-hub scan` then
   discovers new openings weekly (free ATS APIs out of the box; Apify optional).
5. Write your `personal_brand/brand_statement.md` using the included
   Skills x Interests x Market Needs framework.
6. (Optional) Tweak the `/apply` skill so cover letters match your voice.

**Validation:** the AI can build a tailored application for any new role in under
five minutes, using only what is already in your repo.

---

## Folder structure

After `career-hub init`, your data directory looks like this:

```
your-career-hub/
  profiles/             # Your professional profiles (skills, narrative, fit rules)
  cvs/                  # CV templates by role and language
  roles/                # Role families and sectors you target
  work_experience/      # Career history in STAR format with KPIs (single source of truth)
  documentation_hub/    # Past projects as reusable case studies
  certificates/         # Certifications, courses, credentials
  personal_brand/       # Brand statement, voice and tone, content strategy
  applications/         # Generated by /apply, one folder per company
  jobsearch.db          # SQLite tracking of applications and scanned jobs
  portals.yml           # Companies and portals to scan
  config.toml           # Roles, fit thresholds, CV mapping
  CLAUDE.md             # Root AI guide
  START_HERE.md         # 5-minute human quickstart (no AI required)
```

Every folder has its own `CLAUDE.md` that explains its purpose, expected data, and
how an AI should help you fill it.

---

## CLI commands (preview)

```bash
career-hub init                 # initialize a new career-hub data directory
career-hub fit --jd JD.docx --role data --company "Acme"
career-hub apply --role data --company "Acme"
career-hub log --company "Acme" --status applied
career-hub report               # dashboard of all applications
career-hub scan --profile data  # discover new openings (ATS + optional Apify)
```

Full reference is in `docs/` (Phase 4).

---

## Credits and inspiration

- **Original vision:** Luis Fernando Molina ([@fernandosiavato](https://github.com/fernandosiavato)),
  years ago in Notion. The centralized professional life database is the seed of this project.
- **Scanner module:** inspired by Santi Fernandez's
  [career-ops](https://github.com/santifer/career-ops). The "AI proposes, human decides"
  philosophy and the structured ATS scraping approach come from there.

Full acknowledgments in [docs/CREDITS.md](docs/CREDITS.md).

If `career-hub` is useful to you, the best way to support the project is to
[follow @fernandosiavato](https://github.com/fernandosiavato) and star the repo.

---

## License

MIT — see [LICENSE](LICENSE).
