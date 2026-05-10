# /apply — the central application skill

`/apply` is a Claude Code skill that orchestrates a full job application
end to end on top of a career-hub data directory. It is the most-used
piece of career-hub and the one that does the heaviest lifting per
application.

The skill itself lives at `.claude/skills/apply/SKILL.md`. This document
explains what it does, why, and how to extend it.

## What it does in one line

Given a job description and your career-hub data, `/apply` writes the
folder structure for one application: the JD note, a keywords + gaps
file, a fit score, a cover letter in your voice, and a Python script
that builds a tailored CV. You review and submit. It never auto-submits.

## What it reads

Before producing anything, the skill reads the user's data dir:

| Source | Used for |
|--------|----------|
| `profiles/PROFILE_*.md` | YAML frontmatter → fit calculation, skill matching. |
| `work_experience/*/achievements.md` | STAR statements with KPIs → cover letter examples. |
| `personal_brand/voice_and_tone.md` | Writing rules → overrides default voice. |
| `documentation_hub/*` | Case studies → cited in cover letters when relevant. |
| `certificates/*/metadata.yml` | Active credentials → mentioned when JD asks. |
| `config.toml` | Role keys, sector folders, CV template paths. |

If any of these are missing, the skill degrades gracefully (no
work_experience entries means it sticks to the profile narrative; no
voice_and_tone means it uses the default rules in the skill body).

## What it writes

Inside `$JOBSEARCH_DATA_DIR/<role-folder>/<Company - Role>/`:

1. `JD_<Role>_<Company>.md` — normalized JD with metadata header.
2. `CV_Keywords_<Company>.md` — priority keywords, matched skills, gaps,
   recommended CV framing.
3. `Cover_Letter_<Company>_<YYYYMMDD>.md` — 350-500 word letter in the
   user's voice, no em dash, first person, concrete numbers.
4. `gen_cv_<company>.py` (in `cvs/scripts/`) — `python-docx` script that
   the user runs to produce the tailored DOCX.

It also updates `jobsearch.db` to track the application as `pending`.
The user runs `career-hub log --status applied` after submitting.

## Workflow phases

| Phase | Purpose |
|-------|---------|
| 0 | Read the user's career-hub. Stop if not initialized. |
| 1 | Parse the JD: company, role, language, must-haves, nice-to-haves, keywords. |
| 2 | Pick the best profile, compute fit score, classify (apply / apply with gaps / pass). |
| 3 | Ask only what cannot be inferred (one consolidated message via `AskUserQuestion`). |
| 4 | Create the folder and the JD + keywords files. |
| 5 | Generate the cover letter using the user's voice rules. |
| 6 | Generate the CV-tailoring Python script. |
| 7 | Print a summary and the next steps. |

The phases are sequential. The skill does not parallelize them because
later phases depend on choices made earlier (e.g., the cover letter
needs the picked profile from phase 2).

## How to extend the skill

### Add a new profile

Create `$JOBSEARCH_DATA_DIR/profiles/PROFILE_<KEY>.md` with the YAML
frontmatter shown in `templates/profiles/CLAUDE.md`. Add the role to
`config.toml`. The skill picks it up automatically on the next
invocation.

### Override the writing voice

Edit `personal_brand/voice_and_tone.md`. The skill loads it in phase 5
and prefers its rules over the defaults baked into the skill body.

### Change the cover letter structure

Edit `.claude/skills/apply/SKILL.md` (the skill source). The structure
lives in step 5. If you change the section count or order, also update
the example output in step 7 so the summary stays in sync.

### Add a new artifact type

If you want the skill to also produce, say, a one-pager portfolio PDF
per application:

1. Add a new step (e.g., 6.5) in the skill body describing what to
   produce and where to put it.
2. Add the artifact name to the "Files created" list in step 7.
3. If it requires reading a new folder under the data dir, add the
   read to step 0 and create a `CLAUDE.md` for the new folder.

### Replace the CV-script approach with direct DOCX generation

The skill currently writes a Python script that **the user** runs. This
is intentional: it gives the user a chance to read the script and
catch fabrications before producing the DOCX. If you want to skip that
gate, you can change step 6 to invoke `python-docx` directly. Document
the trade-off in the skill body so future contributors understand the
choice.

## Failure modes worth knowing

- **Profile says skill X but no work_experience entry mentions it.** The
  skill will treat X as "claimable but unproven" and will not anchor a
  cover letter sentence on it. Phase 2 surfaces this in the gaps list.
- **JD asks for a hard requirement the user does not have.** Fit drops
  below 60%; the skill asks the user whether to continue before writing
  any files.
- **`config.toml` lists a role with no `PROFILE_*.md` file.** The skill
  reports the misconfiguration and stops, pointing the user at
  `templates/profiles/CLAUDE.md`.
- **`voice_and_tone.md` contradicts itself.** The skill applies the user
  rules first, then the defaults. If both say "always do X" and "never
  do X", the user file wins, but the skill should flag the conflict in
  the summary so the user can fix the file.

## Why "AI proposes, human decides"

career-hub deliberately stops short of submitting. Two reasons:

1. **Quality control.** Cover letters that sound generic get caught
   before going out. Numbers that look wrong get caught before going
   out.
2. **Respect for the channel.** Submitting through someone's ATS without
   them in the loop is bad form and, in some jurisdictions, a violation
   of platform terms.

This stance is inherited from
[career-ops](https://github.com/santifer/career-ops). Do not try to
"fix" it.
