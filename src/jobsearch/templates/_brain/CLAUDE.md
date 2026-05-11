# _brain/ — persistent memory between sessions

This folder holds what the AI needs to remember about you between
conversations. The CLI does not read these files; they exist for any AI agent
that opens your career-hub.

## What lives here

| File | Purpose | Who writes it |
|---|---|---|
| `SESSION_START.md` | Preload checklist the AI reads at the start of every session | You (initially) — rarely edited later |
| `USER_CONTEXT.md` | Canonical facts about you: name, languages, location, modality, salary floor, sectors | You confirm; AI proposes diffs |
| `INSIGHTS.md` | Append-only log of lessons from past postulations | AI writes after tasks; you can edit |

## Two unbreakable rules

1. **`USER_CONTEXT.md` is user-locked.** AI agents must never overwrite it
   without showing you the diff and getting your confirmation first.
2. **`INSIGHTS.md` is append-only.** AI agents add new dated entries but
   never delete or rewrite existing ones. If something becomes outdated, the
   AI writes a new `rule` entry that supersedes it.

## How `career-hub init` treats this folder

The first time you run `career-hub init`, the three files are seeded with
the starter skeletons. On any subsequent run **without `--force`**, the
files are left alone — including `INSIGHTS.md`. That is intentional: a
re-init must not erase what you and the AI have learned.

If you ever do want to reset the brain folder, the safe pattern is:

```
mv _brain/INSIGHTS.md _brain/INSIGHTS.bak.md
career-hub init --force
# inspect, then either restore the backup or discard it
```

## How an AI should read this folder

Always in this order, every session:

1. `USER_CONTEXT.md` (stable facts)
2. Last 20 entries of `INSIGHTS.md` (recent learnings)
3. The active task's folder `CLAUDE.md`

`SESSION_START.md` documents the exact protocol — it is what the AI quotes
when in doubt about how to use this folder.
