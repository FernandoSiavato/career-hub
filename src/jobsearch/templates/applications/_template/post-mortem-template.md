# Application Post-Mortem Template

> **For the AI:** This template runs after an application is submitted (or
> rejected, or converted). The output is a `post_mortem.md` inside the
> `applications/<company>/` folder, plus **one appended entry** to
> `_brain/INSIGHTS.md`. Run iteratively, but post-mortems are short — one
> session.
>
> **Before asking:**
> 1. Read everything already in `applications/<company>/` — the JD, the
>    fit_report, the cover letter, the CV that was submitted, any
>    follow-up notes.
> 2. Read the last 20 entries of `_brain/INSIGHTS.md` so you do not
>    duplicate a learning.
> 3. Ask only the questions that move you toward the INSIGHTS entry at
>    the end. Skip what is already in the files.

---

## 1 — Outcome

- **Final status** (`applied` / `interview` / `technical_test` / `offer` /
  `hired` / `rejected` / `withdrawn` / `ghosted`):
- **Time to first response** (days from submit to first human reply):
- **Total process length** (days from submit to final status):
- **Recruiter or hiring manager feedback** (paste verbatim if you have it
  — direct quotes are gold for the INSIGHTS entry):

## 2 — What worked

- **Which sentence in the cover letter got a reaction** (recruiter quoted
  it, ATM raised it in the call, you noticed the interviewer reading it):
- **Which case study from `documentation_hub/` did the interviewer ask
  about**:
- **Which keyword in the CV survived ATS** (you know if you asked the
  recruiter):
- **Which pre-existing INSIGHT did you apply that helped**:

## 3 — What did not work

- **Skill gap the JD revealed** that your `profiles/PROFILE_*.md` does not
  evidence (could be missing skill, missing years, missing alias):
- **Stack mismatch you only noticed mid-interview**:
- **Modality / salary mismatch** that should have shown up in the
  `fit_report` but didn't:
- **Cover letter line that fell flat** (recruiter ignored or
  misinterpreted):
- **A question you could not answer well** in interview:

## 4 — INSIGHTS commit

This is the only mandatory output. Append one entry to
`_brain/INSIGHTS.md`:

```
## YYYY-MM-DD — pattern | gap | rule

<one paragraph, 60-100 words. Concrete. Reference the company, the role,
the file path or skill if useful. Should fit the tag:
- pattern = something that worked, reuse it on next role of this type
- gap = data missing in the system that hurt; describe what to add and
  where (e.g. "add `dbt` alias to PROFILE_DATA skills; missing in IRC JD
  match")
- rule = a new constraint the user voiced ("never apply to onsite roles
  in Bogotá again" / "always include donor list in NGO letters")>
```

## Output rules

Write `applications/<company>/post_mortem.md`:

```markdown
# Post-mortem: <Company> — <Role>

**Outcome:** <§1 final status>
**Process length:** <§1 days from submit to final>
**Time to first response:** <§1 days>
**Recruiter feedback (verbatim):** <§1>

## What worked
- <§2 list>

## What did not work
- <§3 list>

## Next time, for this kind of role
- <§3 mitigation 1>
- <§3 mitigation 2>

## INSIGHTS entry appended
<paste §4 entry here verbatim so the post-mortem is self-contained>
```

Then open `_brain/INSIGHTS.md` and **append** (do not rewrite) the entry
from §4. One entry per post-mortem, never more. If the lesson is large,
split into 2 entries with different tags.
