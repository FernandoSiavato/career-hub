# CV Structure Template

> **For the AI:** This template plans a base CV DOCX before any
> personalization happens. The output is **not the CV itself** — it is the
> design spec the user follows when they hand-edit the DOCX template under
> `cvs/CV_<ROLE>.docx`. Run iteratively.
>
> **Before asking anything:**
> 1. Read `profiles/PROFILE_<ROLE>.md` for the role being CVed. Use its
>    keywords, achievements, positioning, application_style.
> 2. Read `_brain/USER_CONTEXT.md` for header info (name, contact, links).
> 3. Read `work_experience/` to know what KPIs the bullets can quote.
> 4. If the user has an existing CV (PDF / DOCX / LinkedIn export), ask for
>    the path or paste and start from there. Do not rewrite — extract.
> 5. Probe vague sections. "Summary that sells me" → "Sells you to whom?
>    NGO hiring managers or B2B engineering managers? They want different
>    things."
> 6. Save the plan as `cvs/_template/PLAN_<ROLE>.md` so the user can refer to
>    it when editing the DOCX.

---

## 1 — Existing CV intake

- **Paths to current CVs you have** (PDF / DOCX / LinkedIn export URL):
- **Which one to start from**:
- **Sections in the current CV** (list them in order, e.g. `header → summary
  → experience → education → languages → tools`):
- **What you want to keep verbatim** (some phrases land well — preserve
  them):

## 2 — Audience and section priority

Different audiences read CVs differently. Decide the order.

- **Primary audience** (NGO hiring manager / B2B engineering manager /
  product VP / agency partner):
- **Section order**, top to bottom (rank these — drop the ones you do not
  use):
  - [ ] Header (name, role, contact)
  - [ ] Summary / positioning (3-4 lines)
  - [ ] Key impact / KPIs (3-5 numbers, one line each)
  - [ ] Skills / tools
  - [ ] Experience (most recent first)
  - [ ] Projects / case studies (link to `documentation_hub/`)
  - [ ] Education
  - [ ] Certifications
  - [ ] Languages
- **Page budget**: 1 page (B2B SaaS), 2 pages (NGO / executive), 3+
  (academic / volunteer-heavy)?

## 3 — Header & contact

- **Name format** (full / short / with middle name):
- **Subtitle under the name** (use `cv_subtitle` from PROFILE):
- **Contact channels in order**: email, phone, portfolio, LinkedIn, GitHub,
  city.
- **Photo**: yes / no / regional convention. (NGO Latin America = often yes;
  US tech = no.)

## 4 — Style constraints

- **Font family** (system fonts only for ATS safety: Calibri, Arial, Garamond,
  Cambria):
- **Heading levels** — these matter for the python-docx personalizer. It
  edits **Heading 1** and **Heading 2** safely; bullets in `List Bullet`
  style; body in `Normal`. Anything else may break the script.
- **Bullet format**: `<verb> <object> <metric> <beneficiary>` — the same
  format used in `profiles.achievements`.
- **Colors**: monochrome / one accent color / role-coded? ATS prefers black.
- **KPI block style**: inline in bullets, callout box, or top-of-page table?
  Boxes break ATS — prefer bold inline numbers.

## 5 — DOCX checklist (before you hand off to the personalizer)

The Python script in `cvs/scripts/personalize_cv.py` swaps:

- `<COMPANY>` placeholder in the headline → real company
- The bullet block under a heading named exactly `## Highlights` → top
  matched skills from `fit_analyzer`
- The block under `## Why <COMPANY>` → AI-written sentence

Before you save the template DOCX, confirm:

- [ ] `<COMPANY>` placeholder exists exactly once and in the headline
- [ ] `## Highlights` heading present with 3-5 bullet placeholders
- [ ] `## Why <COMPANY>` heading present with one paragraph placeholder
- [ ] All actual content uses ATS-safe styles (Heading 1/2, Normal, List
      Bullet)
- [ ] No tables for layout, no text-in-image, no header-footer for body text
- [ ] File saved as `cvs/CV_<ROLE>.docx`

## Output rules

When sections 1-5 are filled, write a short plan file
`cvs/_template/PLAN_<ROLE>.md`:

```markdown
# CV plan for <ROLE>

- Audience: <§2>
- Order: <§2 section list>
- Pages: <§2>
- Header: <§3>
- Font / colors: <§4>
- DOCX placeholders in `cvs/CV_<ROLE>.docx`:
  - `<COMPANY>` at: <headline>
  - `## Highlights` at: <line N>
  - `## Why <COMPANY>` at: <line M>
- Notes: <anything else>
```

The plan stays in sync with the DOCX. Update it whenever the structure
changes.
