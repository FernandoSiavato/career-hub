# documentation_hub/ — past projects as reusable case studies

While `work_experience/` describes the **role** you held, this folder
describes specific **projects** you delivered, written in a portfolio-ready
format. The AI cites them as proof of capability when generating cover
letters and answering interviewer questions.

## When to use this folder

Add a case study here when a project meets at least one of:

- It is the strongest example of a skill on your profile.
- It involved an unusual stack or context that is hard to compress into a
  CV bullet.
- You expect to be asked about it in interviews and want a single source
  to refer back to.

Do not document every task. Keep it to your **3-10 strongest projects**.

## File layout

One folder per project:

```
documentation_hub/
  2024_acme_dbt_migration/
    README.md            # overview
    context.md           # what came before, what was broken
    approach.md          # how you decided what to build
    results.md           # KPIs, before/after, who adopted it
    artifacts/           # screenshots, sample SQL, dashboard PDFs
```

Or, for shorter case studies, a single markdown file:

```
documentation_hub/
  2024_acme_dbt_migration.md
  2023_betacorp_onboarding_redesign.md
```

## README.md / single-file template

```markdown
# Project: Acme dbt migration

**When:** Q2-Q3 2024 (4 months)
**Where:** Acme Inc. (employer)
**My role:** lead analyst (1 of 2)

## Problem
Marketing reports took 3 days, broke on every event rename.

## Approach
Modeled events in dbt, version-controlled, schema tests on every model.
Trade-off: slower initial build vs predictable maintenance.

## Result
- Turn-around: 3 days → 2 hours.
- Zero broken reports in 6 months.
- 3 teams adopted the same pattern.
- Executive review meeting cut from 90 to 45 minutes.

## What I would do differently
Start with the dashboards-side first to surface naming conflicts earlier.

## Stack
Postgres, dbt 1.7, GitHub Actions for tests, Looker.
```

## How an AI should help here

- **Writing a case study:** the user describes the project; the AI
  organizes the story into the structure above. Push for the
  "trade-offs" and "what I would do differently" sections — these are
  what differentiate a senior engineer from a juniors one in interviews.
- **Picking a case study to cite:** when the AI is generating a cover
  letter, it should scan this folder, pick the case whose **Result**
  section quotes the highest-impact number relevant to the JD, and link
  to it inside the cover letter without copying the whole thing.
- **Privacy:** if the user wants to publish their career-hub data dir
  (rare but possible), strip employer names and put them in a separate
  `_public/` subfolder rather than editing the originals.
