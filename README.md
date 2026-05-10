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
                │  profiles/  cvs/  work_experience/  │
                │  certificates/  documentation_hub/  │
                │  personal_brand/  applications/     │
                │                                     │
                │       Every folder ships with       │
                │      its own CLAUDE.md guide.       │
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
3. **Folder convention with per-folder `CLAUDE.md`** — every folder explains itself to any AI that opens it. No manual setup of agent context.

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
├── profiles/             # Your professional profiles (skills, narrative, fit rules)
├── cvs/                  # CV templates by role and language
├── roles/                # Role families and sectors you target
├── work_experience/      # Career history in STAR format with KPIs
├── documentation_hub/    # Past projects as reusable case studies
│   └── _template/        # 9-section interview the AI uses with you
├── certificates/         # Certifications, courses, credentials
├── personal_brand/       # Brand statement, voice and tone, content strategy
├── applications/         # Generated, one folder per company
├── jobsearch.db          # SQLite tracker
├── portals.yml           # Companies / ATS to scan
├── config.toml           # Roles, fit threshold, CV mapping
├── CLAUDE.md             # Root AI guide
└── START_HERE.md         # 5-minute human quickstart (no AI required)
```

Every subfolder has a `CLAUDE.md` describing **what lives there, what to expect, and how an AI should help you fill it**. The AI doesn't need extra prompting — opening the folder is enough.

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
