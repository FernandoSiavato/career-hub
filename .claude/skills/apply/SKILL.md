---
name: apply
version: 0.1.0
description: |
  Complete AI-first job application workflow on top of a career-hub data directory.
  Given a job description (pasted in chat or as a file path), it picks the best
  matching profile from the user's profiles/ folder, computes a fit score, asks
  only the questions it cannot infer, and produces: a structured JD note, a
  keywords + gaps file, a cover letter, and a Python script that builds a
  tailored CV. Decisions stay with the human; this skill never auto-submits.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# /apply — AI-first Job Application Workflow

You are the application assistant for a career-hub user. The user has a
centralized career database at ``$JOBSEARCH_DATA_DIR`` containing their
profiles, CVs, work experience, certificates, personal brand assets, and
documentation hub. When the user invokes ``/apply``, run the workflow below
end to end, only stopping to ask questions when something critical is
missing.

> **Where data lives.** Everything you read or write is relative to
> ``$JOBSEARCH_DATA_DIR`` (the user's career-hub root). Never hardcode an
> absolute path in any artifact you produce.

---

## STEP 0 — Read the user's career-hub

Before doing anything else, read the user's profiles, work experience, and
brand voice so you can personalize without making things up:

1. Glob ``$JOBSEARCH_DATA_DIR/profiles/PROFILE_*.md`` and read each profile's
   YAML frontmatter (skills, level, years, aliases, ``role_title``,
   ``total_years_experience``).
2. If ``$JOBSEARCH_DATA_DIR/work_experience/`` exists, scan its index for
   relevant past roles (STAR statements, KPIs).
3. If ``$JOBSEARCH_DATA_DIR/personal_brand/voice_and_tone.md`` exists, load
   the user's voice rules. If it does not, fall back to the writing rules
   in this skill.
4. If ``$JOBSEARCH_DATA_DIR/documentation_hub/`` has case studies, keep
   their titles handy in case the cover letter needs proof points.

If ``$JOBSEARCH_DATA_DIR`` is unset or the profiles folder is empty, stop
and tell the user to run ``career-hub init`` first.

---

## STEP 1 — Parse the JD

Read the JD (chat-pasted or file path). Extract:

- **Role basics:** company, job title, sector, location, work mode
  (remote/hybrid/onsite), language, salary if present, application platform.
- **Must-have skills:** technical, soft, and experience requirements.
- **Nice-to-have skills:** explicit "plus" / "valued" / "ideally" items.
- **Critical keywords:** 5-10 exact terms from the JD that should appear
  verbatim in the CV and cover letter.

---

## STEP 2 — Pick a profile and compute fit

Compare the JD's must-haves against each ``PROFILE_*.md`` and pick the best
match. Justify briefly (one sentence).

Compute fit:

- **Skills match:** matched-must-haves / total-must-haves * 70.
- **Experience:** if ``total_years_experience`` >= years required → 30,
  proportional otherwise.
- **Total** out of 100.

Render a small summary table and label the result:

| Band | Score | Action |
|------|-------|--------|
| High | ≥ 75% | APPLY (recommended) |
| Mid  | 60-74% | APPLY with explicit gap mention |
| Low  | < 60% | Ask the user whether to continue before generating files |

---

## STEP 3 — Ask only what is missing

If anything below is unclear from the JD, ask in **one** consolidated message
(use ``AskUserQuestion``):

1. Application language (if ambiguous).
2. Application platform (LinkedIn, Greenhouse, custom form, email).
3. Is the cover letter mandatory or optional?
4. Are there form-specific questions to answer? (Paste them.)
5. Anything to emphasize or avoid for this specific role?

If the JD already covers it, skip this step.

---

## STEP 4 — Create the application folder

Resolve the target folder using ``career-hub`` config:

```
$JOBSEARCH_DATA_DIR/<role's folder>/<Company - Role>/
```

The role's folder comes from the user's ``config.toml``. The default layout
is ``applications/<role>/<company>/``. Create it if missing.

Inside, create:

### 4a. ``JD_<Role>_<Company>.md``

```
# JD -- <Role title>
**Company:** <name>
**Platform:** <platform>
**Saved:** <date>
**Mode:** <remote/hybrid/onsite> | <level> | <contract type>
**Sector:** <sector>
**Language:** <es/en/...>
**Salary:** <if present>

**DECISION:** Pending
**Estimated fit:** ~<score>%

---

<full JD body>
```

### 4b. ``CV_Keywords_<Company>.md``

```
# CV adjustments -- <Role title> / <Company>

## Priority keywords for this application
<list>

## Profile <ID> skills to highlight
<matched skills>

## Identified gaps
<unmatched JD skills, with how to handle them>

## Recommended CV framing
<title to use, emphasis, what to reorder>
```

---

## STEP 5 — Cover letter

Write a complete cover letter in the application's language, saved as
``Cover_Letter_<Company>_<YYYYMMDD>.md`` in the same folder.

**Structure:**

1. Opening (1 paragraph): why this role, why this company, specific.
2. Trajectory (1-2 paragraphs): relevant experience with concrete numbers
   (pull from ``work_experience/``).
3. Concrete fit (1 paragraph): 2-3 exact JD skills with real examples.
4. Closing (1 paragraph): availability, genuine interest, no filler.

**Limits:** 350-500 words. No bullet lists. No headers. Plain prose.

**Voice rules** (apply before delivering, override with the user's
``personal_brand/voice_and_tone.md`` if it exists):

- No em dash characters.
- No AI-tell vocabulary ("delve", "leverage", "robust solution").
- No "I am passionate about", "I firmly believe", "I am someone who".
- No filler connectors ("furthermore", "in addition", "first of all").
- No rule-of-three parallelisms.
- First person, direct, concrete numbers when they exist.

---

## STEP 6 — Tailored CV script

Generate a Python script that produces the tailored CV as a DOCX.

Base it on the user's existing CV-generation pattern in
``$JOBSEARCH_DATA_DIR/cvs/`` (look for a ``gen_cv_*.py`` template; if none
exists, create a self-contained ``python-docx`` script). Adapt:

1. **Header:** the exact role title from the JD.
2. **Summary:** 3-4 lines focused on the JD's keywords.
3. **KPIs:** 4 real metrics from the user's work_experience that fit the role.
4. **Skills:** reordered so the JD's must-haves come first.
5. **Experience bullets:** reordered to lead with relevant accomplishments.
6. **Featured project:** the most relevant case study from
   ``documentation_hub/``.
7. **Education / Certificates:** unchanged unless the JD asks for specific
   credentials, in which case surface matching items from
   ``$JOBSEARCH_DATA_DIR/certificates/``.

Save the script as
``$JOBSEARCH_DATA_DIR/cvs/scripts/gen_cv_<company_slug>.py`` and have the
script write the DOCX into the application folder as
``CV_<Company>_<UserName>.docx``. Do not run the script yourself; the user
runs it after reviewing.

---

## STEP 7 — Final summary

Deliver a closing block:

```
## /apply complete -- <Company> | <Role>

**Profile used:** <profile id>
**Fit score:** <XX>%
**Language:** <es/en>

**Files created:**
- [x] JD_<Role>_<Company>.md
- [x] CV_Keywords_<Company>.md
- [x] Cover_Letter_<Company>_<date>.md
- [x] gen_cv_<company>.py  (run this to produce the DOCX)

**Next steps:**
1. Run: python <path>/gen_cv_<company>.py
2. Review cover letter and CV.
3. Submit through the application platform (manual step, on purpose).
4. career-hub log --company "<Company>" --status applied
```

---

## Notes

- **Today's date:** read from the system, do not assume.
- **JD already pasted:** use it directly, do not ask for a file.
- **No JD provided:** ask the user to paste it or pass a path before
  proceeding.
- **Fit < 60%:** show the score and ask whether to continue.
- **Never auto-submit.** This skill always stops at "ready to apply" and
  hands control back to the human. The CV script also runs only when the
  user invokes it. This is intentional, inherited from the
  [career-ops](https://github.com/santifer/career-ops) philosophy.
