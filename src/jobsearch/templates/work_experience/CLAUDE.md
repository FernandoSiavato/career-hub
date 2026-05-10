# work_experience/ — your career history (single source of truth)

This folder is the **single source of truth** the AI reads to personalize
applications. Every CV bullet and every cover letter sentence about your
past should trace back to a file here.

If a role you held is not documented here, the AI cannot mention it
without making things up. Treat this folder as the authoritative log of
what you have done.

## File layout

One folder per past role:

```
work_experience/
  2024_acme_data_analyst/
    README.md          # context, dates, scope
    achievements.md    # STAR statements with KPIs
    artifacts/         # screenshots, dashboards, code samples (private)
  2022_betacorp_pm/
    README.md
    achievements.md
```

Folder name convention: `<year-started>_<company-slug>_<role-slug>`. This
sorts naturally by recency and is unambiguous when you change titles
inside the same company.

## README.md per role

```markdown
# Acme — Data Analyst (2024–2025)

**Company:** Acme Inc. (B2B SaaS, 200 employees)
**Role:** Data Analyst, Growth team
**Type:** full-time, remote, USD contract
**Reported to:** VP of Marketing
**Tools:** Postgres, dbt, Looker, Python, Hex

**Scope:** owned the marketing analytics stack — funnel reporting,
campaign attribution, weekly executive review.

**Why I left:** team restructure, role moved to a different city.
```

## achievements.md — STAR with KPIs

Each entry uses **Situation / Task / Action / Result**, with numbers
where they exist. Format the file as one entry per `##` heading:

```markdown
## Migrated marketing analytics from spreadsheets to dbt

**Situation:** weekly funnel reports took 3 days, broke whenever a PM
changed an event name in the product.

**Task:** rebuild the pipeline so reports were reliable and turn-around
under 4 hours, by end of Q2.

**Action:** modeled the event stream in dbt, version-controlled in
GitHub, added 12 schema tests, set up Looker on top.

**Result:** turn-around dropped to 2 hours, zero broken reports in the
6 months that followed, executives started self-serving instead of
asking the analytics team. Adopted by 3 other teams.
```

Aim for 5-10 entries per role. Quality beats quantity.

## How an AI should help here

- **Interviewing for a new entry:** ask the user one role at a time. Use
  STAR explicitly. Push for numbers — if the user says "we improved
  conversion", ask "from what to what, over how long, on what cohort?".
  Do not write the entry until you have at least one number.
- **Tailoring a cover letter:** when generating cover letters, the AI
  picks 1-2 entries that match the JD's must-haves and quotes the
  numbers. It must never invent numbers; if the entry has none, look for
  another entry or fall back to qualitative framing.
- **Detecting gaps:** if a JD asks for X and the user has no
  achievements.md mentioning X, flag it as a real gap (not just a missing
  keyword in the profile).
