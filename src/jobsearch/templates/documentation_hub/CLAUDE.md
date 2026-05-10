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
  _template/
    case-study-template.md         # the structured interview, never edit
  2024_acme_dbt_migration/
    README.md                      # final polished case study
    context.md                     # what came before, what was broken
    approach.md                    # how you decided what to build
    results.md                     # KPIs, before/after, who adopted it
    artifacts/                     # screenshots, sample SQL, dashboard PDFs
```

For shorter case studies, a single markdown file works fine:

```
documentation_hub/
  2024_acme_dbt_migration.md
  2023_betacorp_onboarding_redesign.md
```

## The 9-section template

`_template/case-study-template.md` contains the canonical structure used by
the AI: 9 sections from project context to portfolio metadata, plus an
output-rules block telling the AI how to turn the answers into a polished
case study.

The template is meant to be **filled in iteratively, with the AI as your
interviewer** — not copied blank and stared at.

## How an AI should help here

This is the most important section in this file. Read it before doing
anything.

### Writing a new case study

The user almost never sits down to fill 50 questions. Real flow:

1. **Read what they already have first.** Pull from `work_experience/`,
   any project READMEs in the repo, prior notes, even commit messages or
   LinkedIn posts they paste. Pre-fill every section you can.
2. **Show them what you found** before asking anything new. "I see this
   project in your work_experience as X with metric Y — is that the same
   one?" This earns trust and avoids redundant typing.
3. **Ask only the questions where the answer is missing or shallow.**
   Prioritize the gaps that matter most for interviews:
   - The **problem framing** (Section 2)
   - The **decisions and trade-offs** (Section 3)
   - The **quantified results** (Section 6)
   These are the senior-vs-mid differentiators.
4. **Probe vague answers.** If they say "the system was slow", ask: "Slow
   how — first-byte latency? p95? time-to-render? What was the number
   before and after?" Same for "users were happy", "team adopted it",
   "improved performance".
5. **Offer architecture and diagrams.** If they describe a system in prose
   but never drew it, propose a mermaid component diagram or sequence
   diagram and sketch it in the case study. Architecture diagrams are
   high-leverage portfolio content.
6. **Save progress.** Every few questions, write what you have to the case
   study file. Treat the template as a working document, not a one-shot
   form.
7. **Mark unknowns as `?`.** Never invent metrics, dates, names, or stack
   details. When 80% of the sections are filled and the gaps are minor,
   move to writing the polished case study using the output rules at the
   bottom of the template.

### Picking a case study to cite (during `/apply`)

When generating a cover letter or fit report, scan this folder and pick
the case whose **Result** section quotes the highest-impact number
relevant to the JD. Link to it inside the cover letter without copying
the whole thing.

### Privacy

If the user wants to publish their career-hub data dir (rare but
possible), strip employer names and put them in a `_public/` subfolder
rather than editing the originals. Direct quotes from teammates should
be paraphrased unless the person gave explicit permission to publish.
