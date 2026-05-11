# Role Criteria Template

> **For the AI:** This template defines what the user accepts (and refuses)
> in a target role. The output is `roles/<role>.md` with YAML frontmatter
> read by `fit_analyzer` for the **modality**, **salary_floor**, and
> **sector_fit** scoring dimensions. Run iteratively.
>
> **Before asking anything:**
> 1. Read `_brain/USER_CONTEXT.md` — most defaults live there
>    (`work_modality_preference`, `salary_floor`, `sectors_target`,
>    `sectors_avoid`, `hard_constraints`).
> 2. Read `profiles/PROFILE_<ROLE>.md` for tone and sector context.
> 3. Use USER_CONTEXT as default; only ask when the user wants this role to
>    deviate from the global preference (e.g. global remote-only but willing
>    to commute for one specific company tier).
> 4. Confirm changes back to the user as a diff before writing.

---

## 1 — Sector signals

Goal: what kind of company is a good employer for **this role**.

- **Company size band**: startup (<50), scaleup (50-500), enterprise (500+),
  or sector-specific (NGO, public sector, agency, consultancy):
- **Stage signals** (for startups / scaleups): seed / Series A / B / C+ /
  bootstrapped / non-profit:
- **Industry verticals targeted** (subset of `USER_CONTEXT.sectors_target`):
- **Verticals to avoid** (subset of `USER_CONTEXT.sectors_avoid`):

## 2 — Title aliases

Goal: capture equivalent titles so `fit_analyzer` keyword extraction does
not miss good fits.

- **Canonical title**:
- **Equivalent titles** in EN / ES (recruiters call the same job five
  things):
  - e.g. Data Engineer → `[Analytics Engineer, BI Engineer, Data Platform
    Engineer, Data Platform Specialist]`
  - e.g. MEAL → `[M&E Officer, Indicator Specialist, Monitoring &
    Evaluation Lead]`

## 3 — Must-haves vs nice-to-haves (your filter on top of JD)

JDs have their own must-haves. This section is **your own** filter on top.

- **Must-have for you** (you skip the role if absent): e.g. `4-day week`,
  `equity`, `documented values`, `documented learning budget`, `clear
  promotion ladder`:
- **Nice-to-have**: a wishlist that does not block.
- **Hard constraints** (carry over from `USER_CONTEXT.hard_constraints`,
  add role-specific ones):

## 4 — Red flags in the JD

When you see any of these, the fit goes down regardless of skills match.
Add as many as you want.

- Buzzword density (e.g. `rockstar`, `ninja`, `crusher`, `family vibe`):
- Vague salary (`competitive`, `commensurate with experience`) with no band:
- On-call expectations without explicit comp:
- Unpaid trial tasks beyond a 2-hour limit:
- Non-disclosed recruitment process length:

## 5 — Compensation

These map directly into `salary_floor` and feed the `salary_score` dimension.

- **Currency**:
- **Monthly floor** (below this you decline):
- **Monthly target** (you would happily accept at this number):
- **Equity preference** (none / appreciated / required):
- **Contract type** (full-time / contractor / freelance / mixed):

## 6 — Modality

Maps into `work_modality_preference` and feeds `modality_score`.

- **Modality**: `remote` / `hybrid` / `onsite`
- If `hybrid`: **max days in office per week** (default 2):
- **Geography constraints** (countries you accept work from, time zones
  that work):
- **Relocation**: yes / no / case-by-case:

## Output rules

When sections 1-6 are filled, write `roles/<role>.md` with this frontmatter:

```yaml
---
id: <role_key>           # same as PROFILE_<ROLE>.md id
canonical_title: <§2>
title_aliases: [<§2>]
company_size_target: [<§1>]
sectors_target: [<§1>]
sectors_avoid: [<§1>]
must_have: [<§3>]
nice_to_have: [<§3>]
hard_constraints: [<§3>]
red_flags: [<§4>]
salary_floor:
  - currency: <§5>
    monthly: <§5>
salary_target:
  - currency: <§5>
    monthly: <§5>
equity_preference: <§5>
contract_types: [<§5>]
work_modality_preference: <§6>
hybrid_days_max: <§6>
geo_accepted: [<§6>]
relocation: <§6>
---

# Role filter: <canonical_title>

<Optional 100-200 word narrative: why this role, why these constraints, how
this differs from the user's global preferences in USER_CONTEXT.>
```

If a value is the same as USER_CONTEXT, omit it from the role file — the
fit_analyzer will fall back to USER_CONTEXT automatically. Only include
role-specific overrides.
