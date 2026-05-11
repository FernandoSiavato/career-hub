# Profile Interview Template

> **For the AI:** This template builds or refreshes a `PROFILE_<ROLE>.md` file
> for one role the user targets. The output is YAML frontmatter + a short
> narrative paragraph at the bottom. Run this iteratively, not as a form.
>
> **Before asking anything:**
> 1. Scan `work_experience/` and `documentation_hub/` — extract skills, years,
>    tools, KPIs that already exist there.
> 2. Read `_brain/USER_CONTEXT.md` — name, languages, primary role.
> 3. If a `PROFILE_<ROLE>.md` already exists for the role being interviewed,
>    read it and treat the answers as the starting point. Only revisit the
>    sections that look thin or stale.
> 4. **Show the user what you already have** before asking new questions.
>    "I see Python claimed at level 4 with 3 years from the WV experience.
>    Confirm or adjust?"
> 5. Probe vague answers. "Comfortable with SQL" → "Have you written window
>    functions on tables > 10M rows? Tuned slow queries with EXPLAIN?"
> 6. Never invent skills, years, KPIs, or aliases the user did not give you.
> 7. Mark unknown values as `?` and ask in a later session.
> 8. Save progress after every section — write to `PROFILE_<ROLE>.md` so the
>    user can stop and resume.

---

## 1 — Identity & language

Goal: top-of-frontmatter fields.

- **Target role title** (e.g. "Data Analyst", "MEAL Specialist"):
- **Secondary title for CV subtitle** (often the bridge role you are moving
  toward, e.g. "Data Engineer"):
- **Primary language for applications** (`es` / `en`):
- **Secondary language**:
- **English level** with calibration anchor:
  - 5 / C2 — can negotiate contracts, write thought-leadership in EN
  - 4 / B2 — comfortable in interviews, technical writing, daily standups
  - 3 / B1 — can follow conversations, prepare scripted answers
  - 2 / A2 — read docs, basic email
  - 1 / A1 — minimal
- **Tone of voice for this profile** (`humanitarian_professional`,
  `b2b_consultative`, `technical_pragmatic`, `creative_direct`, custom):

## 2 — Skills inventory

Goal: 10-15 skills with category, level, years, aliases.

For each skill ask:
- **Name** (canonical form — what you would write on a CV):
- **Category** (`technical` / `tool` / `soft` / `language` / `sector`):
- **Level 1-5** with anchors:
  - 5 = "I would teach this to others; recruiters quote me on it"
  - 4 = "I lead projects using this without supervision"
  - 3 = "I deliver with it; need to look up advanced topics"
  - 2 = "I have used it but would not lead with it"
  - 1 = "Aware, not productive"
- **Years actually doing it on a job**:
- **Aliases recruiters use in JDs** (recruiters write the same thing five
  ways — capture them all):
  - e.g. `Power BI` → `[powerbi, power-bi, ms power bi]`
  - e.g. `SQL` → `[postgresql, mysql, bigquery, tsql]`

> Probe gaps the user listed but cannot evidence in work_experience. If they
> say "Python level 4 with 4 years" but the role files only quote 2 years of
> Python use, surface it: "Want me to mark this as `?` until we add a
> work_experience entry that proves the 4 years?"

## 3 — Years & domains

- **Total years experience for this profile** (decimal allowed, e.g. 4.5):
- **Domains held** (NGO / B2B SaaS / consulting / e-commerce / public sector
  / agency / etc.):
- **Domains wanted next** (the bridge — same as `sectors_target` in
  USER_CONTEXT but filtered to this role):

## 4 — Keywords

Goal: 8-12 phrases that should always surface in the CV/letter for this
profile so ATS systems and recruiters recognize you fast.

- **Hard keywords** (tools and frameworks recruiters search):
- **Soft keywords** (responsibilities and verbs: "stakeholder management",
  "indicator design", "pipeline ownership"):
- **Sector keywords** (`humanitarian`, `BHA donor`, `KoboToolbox`, `B2B SaaS`,
  etc.):

## 5 — Positioning & differentiators

- **One-sentence pitch** in the form "I help X do Y using Z because W":
- **Top 3 differentiators** (what you do that the average person in this
  role does not):
- **What you refuse to do** (e.g. on-call, manual data entry, sales calls):
- **2-3 signature achievements** for this role, each with a number and a
  beneficiary. These will land in the `achievements` frontmatter and the AI
  will quote them verbatim in cover letters. Format:
  - `<verb> <object> <metric> <beneficiary>`
  - Example: "Built a Power BI indicator system that cut multi-donor monthly
    reporting from 3 days to 4 hours for the WV operations team"

## 6 — Application style

- **Letter length you prefer** (300 / 500 / 700 words):
- **Opener style** ("formal greeting", "problem-first", "first-person
  story"):
- **Always include** (e.g. "country count", "donor names", "stack list"):
- **Never include** (e.g. em dashes, "passionate about", "synergy"):
- **Sample paragraph you wrote yourself** that the AI should use as the
  voice anchor (paste it; the AI extracts patterns):

## 7 — Output rules

When sections 1-6 are ≥80% complete, write the file at
`profiles/PROFILE_<ROLE>.md` with this structure:

```markdown
---
id: <role_key>
name: <name from USER_CONTEXT>
role_title: <from §1>
secondary_title: <from §1>
language: <from §1>
secondary_language: <from §1>
english_level: <1-5>

total_years_experience: <from §3>

template_map:
  <lang>: "cvs/CV_<ROLE>.docx"

keywords:
  - <from §4>

skills:
  - name: <from §2>
    category: <from §2>
    level: <1-5>
    years: <number>
    aliases: [<list>]
  # ... repeat

achievements:
  - "<from §5 signature 1>"
  - "<from §5 signature 2>"

positioning: >
  <from §5 one-sentence pitch>

tone: <from §1>
sectors: [<from §3 + USER_CONTEXT sectors_target>]
application_style: >
  <2-3 sentences from §6 — length, opener, always/never lists>
---

# <name> — <role_title>

<150-300 word narrative in first person. Mention 2-3 differentiators from
§5 and one signature achievement. End with what you want next.>
```

If a section is incomplete, write `?` in that field and continue. The user
can fill the gaps in a later session.

Never invent skills, years, KPIs or aliases that the user did not provide.
