# roles/ — role-family definitions

This folder is **optional**. Use it when you target multiple sectors with
overlapping but distinct expectations and you want a place to write down
the criteria you use to decide whether a role is worth applying for.

If you only have a couple of roles and `config.toml` is enough, leave
this folder empty. The CLI does not require any specific files here.

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
