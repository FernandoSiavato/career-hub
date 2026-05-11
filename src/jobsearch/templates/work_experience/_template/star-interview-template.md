# STAR Interview Template

> **For the AI:** This template documents one past role using STAR
> (Situation, Task, Action, Result) with KPI probes. The output is a
> `work_experience/<NN>_<company>_<role>_<year>/` folder with a
> `WORK_EXPERIENCE.md` (YAML frontmatter + STAR markdown) and optionally an
> `achievements.md` with 5-10 entries. Run iteratively.
>
> **Before asking anything:**
> 1. Read `profiles/PROFILE_*.md` — the user's tool stack and positioning.
>    Match the role's stack to those skills so years and aliases stay
>    consistent.
> 2. Scan the folder for an existing draft. If `WORK_EXPERIENCE.md` already
>    exists, treat it as starting point. Only refresh thin sections.
> 3. **Probe relentlessly for numbers.** "I improved the dashboard" →
>    "improved from what to what, over how long, on what cohort, measured
>    how?" If the user does not have the number, mark `?` and move on.
> 4. One role per session. Five to ten STAR entries per role is the sweet
>    spot.
> 5. Never invent KPIs, dates, donor names, or stack details.

---

## 1 — Role frame

- **Company**:
- **Role title** (canonical and the version on the contract if different):
- **Type** (full-time / part-time / contractor / volunteer):
- **Start date** (YYYY-MM):
- **End date** (YYYY-MM or `present`):
- **Location** (city, country):
- **Modality** (`remote` / `hybrid (N days)` / `onsite`):
- **Reports to** (role, not name):
- **Team size and scope** (e.g. "team of 4 analysts; data for 3 country
  offices; donors: USAID, BHA"):
- **Which user profile this role maps to** (`meal` / `data` / `product` /
  …):

## 2 — Top 5 achievements (STAR + KPI probes)

For each achievement, the AI asks:

- **Situation** — the operating context. Be specific: what was broken, what
  was the cost of inaction, who was affected.
- **Task** — what you were asked to do (or chose to do).
- **Action** — what you actually did. Verbs in first person. Tools used go
  in §3.
- **Result** — the number. From what to what, over how long, measured how.

**KPI probes to push when the result is vague:**

- "Faster" → faster by how much, on what cohort, who measured?
- "Adopted by the team" → how many people, sustained for how long?
- "Saved time" → how many hours per week, multiplied by what hourly cost?
- "Bigger" → before-number, after-number, % delta?
- "More accurate" → error rate before vs after, on what sample?

Use one block per achievement:

```
### <verb> <object> <metric>

**Situation:**
**Task:**
**Action:**
**Result:**  <number from → number to, over N weeks, measured by X>
**Tools used:** [<list>]
**Beneficiary:** <role / team / org>
```

## 3 — Tools used daily on this role

Important — this feeds back into `PROFILE_*.md` skill years.

- **Tools and frameworks**:
- **Programming languages**:
- **Cloud / infra**:
- **Databases**:
- **Domain tools** (KoboToolbox, Salesforce, dbt, Looker, etc.):

For each tool, note how many of the role's months you actually used it
**daily** (vs occasional). The AI will reconcile this with
`PROFILE_*.md::skills[].years`.

## 4 — Non-technical wins

These rarely make CVs but they make cover letters credible.

- **Communication moment** (a conversation that unblocked something):
- **Leadership moment** (you organized people, not just code):
- **Process moment** (you changed how the team works, not just what they
  ship):
- **Failure recovered** (something went wrong, you owned it):

## 5 — Why I left (or am leaving)

For your own notes only — the AI does not put this in cover letters
verbatim. It surfaces here so the AI can keep cover letter narratives
coherent across roles.

- **What you missed in this role**:
- **What you want next that this role could not give**:
- **What you would do over if you had the chance**:

## Output rules

Write the role at `work_experience/<NN>_<slug>/WORK_EXPERIENCE.md`:

```yaml
---
id: <slug>
empresa: <§1 Company>
cargo_es: <§1 Role ES>
cargo_en: <§1 Role EN>
tipo: <§1 Type>
ubicacion: <§1 Location>
modalidad: <§1 Modality>
fecha_inicio: <§1 Start>
fecha_fin: <§1 End>
perfil: <§1 Profile key>
skills: [<§3 tools>]
---

# <Company> — <Role>

## Role summary

<2-3 lines: scope, team, donors / clients, defining feature of the role>

## Achievements

<5-10 STAR blocks from §2, ordered by impact>

## Non-technical wins

<bullet list from §4>

## Notes

<from §5 (kept for AI continuity, never quoted verbatim)>
```

If achievements are many, split them into a sibling `achievements.md` and
link from `WORK_EXPERIENCE.md`.

Each STAR entry's `Result` line **must** have a real number or be marked
`?` for follow-up. Cover letters never quote `?` lines.
