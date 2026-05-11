<div align="center">

# career-hub

**Your professional life as a queryable database — AI builds the applications.**

[![CI](https://github.com/FernandoSiavato/career-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/FernandoSiavato/career-hub/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/career-hub.svg)](https://pypi.org/project/career-hub/)
[![Python versions](https://img.shields.io/pypi/pyversions/career-hub.svg)](https://pypi.org/project/career-hub/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/career-hub)](https://pepy.tech/project/career-hub)
[![Status](https://img.shields.io/badge/status-alpha-orange)](CHANGELOG.md)
[![Follow](https://img.shields.io/github/followers/FernandoSiavato?style=social&label=Follow%20%40fernandosiavato)](https://github.com/FernandoSiavato)
[![Star](https://img.shields.io/github/stars/FernandoSiavato/career-hub?style=social)](https://github.com/FernandoSiavato/career-hub)

[Quickstart](#-quickstart) · [The 3 pillars](#-the-3-pillars) · [How it works](#-how-it-works) · [Levels](#-the-3-levels) · [FAQ](#-faq) · [Roadmap](#-roadmap)

</div>

---

## Why this exists

You rewrite your career story for every job application. Match keywords. Translate the cover letter. Tweak the CV bullets. Re-find the certificate. Re-explain the project. Every. Time.

`career-hub` is the AI-first solution to that loop: a **local, structured database of your professional life** — profiles, CVs, work experience, certificates, project case studies, brand — where any AI agent (Claude, ChatGPT, your own) has full read access and can assemble a tailored application in minutes instead of hours.

You own the data. It lives on your disk. The AI just reads it.

---

## ⚡ Quickstart

```bash
# 1. Install
pip install career-hub

# 2. Provision your data directory
career-hub init --data-dir ~/career-hub
export JOBSEARCH_DATA_DIR=~/career-hub      # PowerShell: $env:JOBSEARCH_DATA_DIR="..."

# 3. Open the folder in Claude Code, paste a job description, and run:
/apply
```

That's it. The AI reads your profile, picks the right CV, builds a cover letter in your voice, calculates a fit score, and creates an `applications/<company>/` folder with everything ready to submit.

**First-time setup walkthrough:** open the folder in Claude Code and say *"explain this project and walk me through onboarding"*. The root `CLAUDE.md` will guide the AI.

---

## 🧱 The 3 pillars

```
                ┌─────────────────────────────────────┐
                │      Your career data directory     │
                │  _brain/  profiles/  cvs/  roles/   │
                │  work_experience/  certificates/    │
                │  documentation_hub/  personal_brand/│
                │  applications/                      │
                │                                     │
                │       Every folder ships with       │
                │   its own CLAUDE.md + _template/    │
                │     (a structured question bank).   │
                └────────┬────────────────────┬───────┘
                         │                    │
                         ▼                    ▼
            ┌────────────────────┐   ┌─────────────────────┐
            │  Python CLI        │   │  Claude Code skill  │
            │  ``career-hub``    │   │  ``/apply``         │
            │                    │   │                     │
            │  fit · cover_letter│   │  reads JD → picks   │
            │  cv-personalize    │   │  profile → builds   │
            │  scan (ATS+Apify)  │   │  full application   │
            │  report · log      │   │  package            │
            └────────────────────┘   └─────────────────────┘
```

1. **CLI `career-hub`** — fit analysis, CV personalization, cover letter, optional dynamic job scanning across ATS portals (Greenhouse, Ashby, Lever, Apify).
2. **Skill `/apply`** for Claude Code — orchestrates a full application end to end: reads the JD, picks the right profile, calculates a fit score, generates the cover letter and a CV-tailoring script, and only asks you for the data it cannot infer.
3. **Folder convention with per-folder `CLAUDE.md` + `_template/` question banks** — every folder explains itself to any AI that opens it. The AI runs the templates as iterative interviews rather than blank forms.

## 🧠 What's new in v2

- **`_brain/` folder** — persistent memory between AI sessions. `SESSION_START.md` is the preload checklist, `USER_CONTEXT.md` is the canonical user record, `INSIGHTS.md` is an append-only log of patterns the AI learns from each postulation.
- **One `_template/` per folder** — every folder ships a structured question bank (profile, STAR interview, CV planning, role criteria, brand discovery, voice & tone, content strategy, certificate intake, application post-mortem, case study). The AI runs them iteratively: read first, ask only the gaps, probe vague answers, never invent.
- **Custom fit scoring** — `[scoring.weights]` in `config.toml` lets you weigh **skills**, **experience**, **modality**, **salary_floor**, and **sector_fit**. The analyzer auto-extracts modality / salary / sector signals from the JD and combines them with your filters from `roles/<role>.md` and `_brain/USER_CONTEXT.md`. Dimensions the JD does not mention are dropped and their weight is redistributed — every score is explainable.
- **Phase-based onboarding** — `START_HERE.md` walks new users through Phases 0-5 (wire the brain → epicenter profile → STAR history → voice → custom scoring → apply & log) with explicit success indicators per phase.

---

## 🔍 How it works

| Stage | What happens | What you do |
|---|---|---|
| **Read** | The AI loads your profiles, work experience, certificates and brand from your data dir. | Nothing — your data is already there. |
| **Match** | `fit_analyzer` extracts required skills from the JD, fuzzy-matches against your profile, and scores 0-100. | Paste the JD into the chat or save it as `JOB.docx` in a company folder. |
| **Compose** | The skill picks the strongest case studies from `documentation_hub/`, writes a cover letter in your voice, and emits a Python script that personalizes your CV template. | Review the score, the gaps, the letter draft. |
| **Apply** | You run the CV script, submit manually on the company portal. **No auto-submission** — the human always decides. | Click submit. Run `career-hub log --status applied`. |
| **Track** | SQLite database stores every application, status, fit score, and detected gap. | `career-hub report` to see your dashboard, your skill gaps across all JDs, and recent activity. |

---

## 📁 What's inside your data directory

After `career-hub init`:

```
your-career-hub/
├── _brain/                # Persistent AI memory (SESSION_START, USER_CONTEXT, INSIGHTS)
├── profiles/              # The epicenter: skills, narrative, fit rules per role
│   └── _template/         # Profile interview question bank (7 sections)
├── cvs/                   # CV templates by role and language
│   └── _template/         # CV structure planning template
├── roles/                 # Role-specific filters: modality, salary, sectors
│   └── _template/         # Role criteria question bank
├── work_experience/       # Career history in STAR format with KPIs
│   └── _template/         # STAR interview template (per-role)
├── documentation_hub/     # Past projects as reusable case studies
│   └── _template/         # 9-section case-study interview
├── certificates/          # Certifications, courses, credentials
│   └── _template/         # Certificate intake question bank
├── personal_brand/        # Brand statement, voice and tone, content strategy
│   └── _template/         # 3 interviews: discovery, voice, strategy
├── applications/          # Generated, one folder per company
│   └── _template/         # Post-mortem template (feeds INSIGHTS.md)
├── jobsearch.db           # SQLite tracker
├── portals.yml            # Companies / ATS to scan
├── config.toml            # Roles, fit threshold, custom scoring weights
├── CLAUDE.md              # Root AI guide (session preload + folder tour)
└── START_HERE.md          # Phase-based onboarding (no AI required)
```

Every subfolder has a `CLAUDE.md` describing **what lives there, what to expect, and how an AI should help you fill it** — plus a `_template/` with the structured question bank the AI runs as an iterative interview.

---

## 🎯 The 3 levels

`career-hub` is designed to grow with you. You don't fill everything on day one.

| Level | Time | Outcome |
|---|---|---|
| **1. Setup** | 15 min | `career-hub init` ran, AI greeted you, `career-hub report` shows zero applications. |
| **2. First application** | 1-2 h | One real profile written, one real `/apply` ran, one `applications/<company>/` folder with 5 generated files. |
| **3. Full system** | 1-2 weeks | `work_experience/` complete (5+ roles, STAR + KPIs), 3-5 case studies in `documentation_hub/`, `personal_brand/brand_statement.md` published. The AI can now build any application in < 5 minutes. |

Each level is documented in the root `CLAUDE.md` so any AI you open the folder with can walk you through it.

---

## 🛠️ CLI reference

```bash
career-hub init [--data-dir PATH] [--force]
career-hub fit --jd JD.docx --role data --company "Acme"
career-hub apply --role data --company "Acme"      # creates folder, CV, cover letter
career-hub log --company "Acme" --status applied
career-hub report                                   # dashboard + skill gaps
career-hub scan --profile data                      # ATS + Apify discovery
career-hub scanned --profile data                   # list discovered jobs
career-hub fit-scanned --profile data               # batch fit on discovered jobs
career-hub web                                      # local dashboard at :8765
```

Full architectural overview: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
Skill `/apply` deep dive: [docs/SKILL_APPLY.md](docs/SKILL_APPLY.md).
Scanner: [docs/SCANNER.md](docs/SCANNER.md).

---

## ❓ FAQ

**Does career-hub send my data anywhere?**
No. Everything is local: SQLite, files on disk, env vars. The AI that helps you is whatever client you choose (Claude Code, ChatGPT, etc.) — `career-hub` never makes outbound calls except when **you** explicitly run `scan` against an ATS or Apify.

**Why not just keep my CV in Google Docs?**
Because a CV is the *output*, not the source. With `career-hub` the source is structured (skills with levels and aliases, work experience in STAR format, projects as reusable case studies). The CV, the cover letter and the LinkedIn post are all generated views over that source.

**Will it auto-apply for me?**
No, by design. The skill `/apply` produces the artifacts; **you** submit. Auto-submission is the one thing this project will never merge — see [CONTRIBUTING.md](CONTRIBUTING.md).

**Do I need Claude Code specifically?**
No. The CLI works standalone. The folder convention works with any AI that reads markdown. Claude Code happens to be where the `/apply` skill runs natively, but the underlying scripts are pure Python.

**Apify is paid — is the scanner usable for free?**
Yes. The Greenhouse / Ashby / Lever scrapers are free and cover a huge portion of the startup market. Apify is only needed for LinkedIn, Indeed, ReliefWeb, Workable.

---

## 🗺️ Roadmap

Current status: **alpha**. Local install works (`pip install -e .`), 55 tests passing, CI green on Python 3.10/3.11/3.12 across ubuntu + windows. PyPI publication pending v0.1.0 release.

Tracked progress in [CHANGELOG.md](CHANGELOG.md). Phase plan:

- [x] **Phase 1** — Repo scaffold, license, README, vendored CLI
- [x] **Phase 2** — Path abstraction, PII removal, dynamic roles via `config.toml`
- [x] **Phase 3** — pip packaging, `career-hub init` command
- [x] **Phase 4** — Per-folder `CLAUDE.md` guides, deep docs
- [x] **Phase 5** — Tests, CI, release workflow, issue templates
- [ ] **v0.1.0** — First PyPI release

---

## 🤝 Contributing

PRs, issues and ideas welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, the lint and test loop, and the conventions for adding new roles, skills or scanners.

Community standards: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) (Contributor Covenant 2.1).

---

## 💛 Credits

- **Original vision and maintainer:** Luis Fernando Molina ([@fernandosiavato](https://github.com/fernandosiavato)). The centralized professional-life database started years ago as a Notion workspace; this is the open-source extraction.
- **Scanner inspiration:** Santi Fernandez's [career-ops](https://github.com/santifer/career-ops). The "AI proposes, human decides" philosophy and the structured ATS scraping approach come from there.

Full acknowledgments in [docs/CREDITS.md](docs/CREDITS.md).

If `career-hub` saves you time, the best support is to [follow @fernandosiavato](https://github.com/FernandoSiavato) and star the repo.

---

## License

[MIT](LICENSE).
