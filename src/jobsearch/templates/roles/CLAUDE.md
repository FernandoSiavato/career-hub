# roles/ — the filters

This folder defines what the user accepts (and refuses) per role. The
files here also feed the custom-scoring dimensions of `career-hub fit`:
**modality**, **salary_floor**, and **sector_fit**. Each role file can
override the global defaults in `_brain/USER_CONTEXT.md` for that
specific role only.

If a value matches `USER_CONTEXT.md`, **do not** repeat it in the role
file — the fit analyzer falls back to USER_CONTEXT automatically. The
role file should contain only overrides.

## Use the question bank

When the user wants to define or refine a role's filters, open
**`_template/role-criteria-template.md`** and run it iteratively.
Pre-fill from USER_CONTEXT first; only ask the questions where the user
deviates from their global preferences.

The output is a `roles/<role>.md` with YAML frontmatter the
`fit_analyzer` reads via `profiles.load_role_filters(role)`.

## What to put here

One markdown file per role family or sector you target. Examples:

```
roles/
  data.md              # Data analyst / engineer / scientist
  product.md           # Product manager
  meal.md              # Monitoring & evaluation (NGO sector)
  growth.md            # Growth / lifecycle marketing
```

Each file can contain:

- **Sector signals**: what kinds of companies, sizes, stages you target.
- **Title aliases**: titles that mean the same thing across companies
  (e.g. "Data Analyst" = "Analytics Engineer (junior)" = "BI Specialist").
- **Must-haves vs nice-to-haves**: your personal filters, separate from
  the JD.
- **Red flags**: anything that should auto-reject (no remote, no salary,
  toxic words like "ninja", "rockstar", etc.).
- **Compensation expectations**: floor for this role family.

## How an AI should help here

When the user asks "should I apply to this?", read the relevant role
file and the JD, then return a structured comparison:

| Criterion | Your filter | JD says | Match |
|-----------|-------------|---------|-------|
| Remote ok | yes | hybrid 3 days | ⚠ |
| Salary floor | $80k | not stated | ? |
| Stack | Postgres + dbt | MySQL + Looker | ⚠ |

Then give a single recommendation: `apply` / `apply with caveats` / `pass`.

## Why this is separate from `profiles/`

`profiles/` describes what you can do.
`roles/` describes what you want to do.

They overlap but are not the same. A profile of yours might fit a JD
mechanically (skills match) while the role itself fails your `roles/*.md`
filters. Keeping them separate avoids confusing fit-the-skills with
fit-the-life.
