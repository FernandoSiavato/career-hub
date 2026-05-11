# career-hub — your professional life, centralized

This folder is the data root of a career-hub installation. It is the single
place from which any AI agent can read your career history and help you
ship job applications without rewriting your story every time.

## Session preload (READ FIRST, every session)

Before you answer anything or take any action in this folder:

1. Read **`_brain/SESSION_START.md`** — the preload checklist.
2. Read **`_brain/USER_CONTEXT.md`** — canonical facts about the user
   (name, languages, location, modality, salary floor, target sectors).
3. Read the last 20 entries of **`_brain/INSIGHTS.md`** — lessons saved
   from past postulations.

Then proceed with the user's request. Detailed rules for reading and
writing the brain folder live in `_brain/CLAUDE.md`.

## A reading-order tour of this directory

The folders below are listed in the order it makes sense to fill them.
The goal is a coherent professional story: identity → past → voice →
direction → output.

1. **`_brain/`** — persistent memory between sessions (start here).
2. **`profiles/`** — the epicenter. Each `PROFILE_<ROLE>.md` is the
   single document the CLI loads when scoring a JD and generating
   applications.
3. **`work_experience/`** — the proof. STAR achievements with KPIs the
   AI quotes verbatim in cover letters.
4. **`documentation_hub/`** — the portfolio. Deep case studies (9-section
   template) the AI cites in interviews and letters.
5. **`personal_brand/`** — the voice. Brand statement, voice & tone
   rules, content strategy. The AI applies the voice rules to every
   piece of writing it produces for you.
6. **`certificates/`** — the credentials. Metadata + PDFs. Surfaces in
   cover letters when the JD asks for a specific credential.
7. **`roles/`** — the filters. What you accept and refuse, per role.
   Feeds the modality / salary / sector dimensions of the fit score.
8. **`cvs/`** — the templates. DOCX base CVs by role and language. The
   personalizer copies one of these per application.
9. **`applications/`** — the output. One folder per company. Generated
   by `career-hub apply`. Post-mortem files here feed `INSIGHTS.md`.

Every folder ships with its own `CLAUDE.md` (describing the folder) and a
`_template/` subdirectory (a question bank the AI uses to interview the
user iteratively).

## Custom fit scoring

`career-hub fit` weighs five dimensions: **skills**, **experience**,
**modality**, **salary_floor**, **sector_fit**. The weights live in
`config.toml` under `[scoring.weights]`. Weights need not sum to 1.0; the
analyzer normalizes them. If a JD lacks a signal (e.g. salary not
disclosed), that dimension is dropped and its weight is redistributed
across the dimensions actually scored. The `FitReport` records which
dimensions contributed and the normalized weights used, so every score is
explainable.

To change the system's defaults: edit `config.toml [scoring.weights]`.
To override per-role (e.g. accept hybrid for `data` only), write a
`roles/<role>.md` with the differing fields — values not redeclared fall
back to `_brain/USER_CONTEXT.md`.

## Working with the user — protocol

1. **Bootstrapping a new user.** If `USER_CONTEXT.md` still has
   `<placeholders>`, the user has not done Phase 0. Offer to walk them
   through the five phases of `START_HERE.md`. Phase 0 takes five minutes.
2. **Interviewing.** Every folder's `_template/` is a structured
   question bank. Run it iteratively — read what the user already has,
   ask only what is missing or shallow, probe vague answers for
   numbers, never invent. Save progress between sections.
3. **Generating applications.** Use the `/apply` skill (Claude Code) or
   the CLI `career-hub apply`. The skill reads `profiles/`, picks the
   strongest case study from `documentation_hub/`, writes the cover
   letter applying `personal_brand/voice_and_tone.md`, and lets the
   user submit. **Never auto-submit.**
4. **After an application reaches a final status.** Run the post-mortem
   template in `applications/_template/`. Append one dated entry to
   `_brain/INSIGHTS.md`. Next session, you read it.

## Privacy

Everything in this folder is the user's data. The default `.gitignore`
excludes `*.db` and `.env`. If the user commits this folder to a git
repo, surface that risk before pushing.

## CLI quick reference

```
career-hub fit --jd JOB.docx --role data --company "Acme"
career-hub apply --role data --company "Acme"
career-hub log --company "Acme" --status applied
career-hub report
career-hub scan --profile data
```

Full docs: <https://github.com/fernandosiavato/career-hub> (or the
`docs/` folder in the source checkout).
