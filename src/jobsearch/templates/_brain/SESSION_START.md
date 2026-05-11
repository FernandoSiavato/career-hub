# SESSION_START — read this first, every session

You are an AI agent helping a user with career-hub. Before you answer any
question or take any action, follow this preload checklist. It exists so the
user does not have to re-explain themselves every conversation.

## 1. Read in order

1. **`_brain/USER_CONTEXT.md`** — the canonical record of who the user is
   (name, languages, location, modality preference, salary floor, target
   sectors, hard constraints). Treat it as source of truth for stable facts.
2. **`_brain/INSIGHTS.md`** — read the **last 20 entries** only. They contain
   lessons the AI (you, in past sessions) saved after completed tasks. Weight
   recent entries over old ones.
3. **The active folder's `CLAUDE.md`** — for the specific task at hand
   (`profiles/`, `work_experience/`, `applications/`, etc.).

If any of these files is missing, the user has not gone through Phase 0 yet.
Offer to run Phase 0 from `START_HERE.md`.

## 2. Two unbreakable rules

- **`USER_CONTEXT.md` is user-locked.** Never write to it without the user
  explicitly confirming the diff first. Propose changes as a diff, wait for
  approval, then write.
- **`INSIGHTS.md` is append-only.** Never delete or rewrite existing entries.
  Add one new entry after a completed task: dated header, one paragraph,
  tagged as `pattern`, `gap`, or `rule`. Format below.

## 3. INSIGHTS entry format

```
## YYYY-MM-DD — pattern | gap | rule

One paragraph: what happened, what was learned, when to apply it next time.
Keep it concrete. Reference the company, the role, the file path if useful.
```

`pattern` = something that worked and should be reused.
`gap` = something missing in the user's data that hurt the application.
`rule` = a new constraint the user voiced ("never apply to onsite roles in X").

## 4. Map of user triggers to actions

When the user says any of these, you already know what they want:

| User says | What you do |
|---|---|
| "interview me for my profile" | Open `profiles/_template/profile-interview-template.md`, run sections 1-7, pre-filling from `work_experience/` and `documentation_hub/` |
| "let's document a role" | Open `work_experience/_template/star-interview-template.md`, one role at a time |
| "post-mortem on \<company\>" | Open `applications/<company>/`, run `applications/_template/post-mortem-template.md`, then append an INSIGHTS entry |
| "fit this JD" | Run `career-hub fit --jd ... --role ...`, then explain the score and the gaps |
| "review my letter" | Read `personal_brand/voice_and_tone.md` first, then read the draft, then suggest line-level edits matching the user's voice |
| "what's missing" | Cross-check `profiles/PROFILE_*.md` against `work_experience/` — surface skills claimed but unproven, KPIs missing, gaps to fill |

## 5. Bootstrapping a brand-new user

If `USER_CONTEXT.md` still contains only placeholders (look for `<your-...>`
strings), the user has not run Phase 0. Do not pretend you know them. Ask:

> "I see your USER_CONTEXT is still the starter skeleton. Want to do a quick
> 5-minute Phase 0 so I know who you are before we go further?"

Then walk them through Phase 0 from `START_HERE.md`.

## 6. End of session

Before ending a substantial task, ask yourself:

- Did I learn something the user will want me to remember next time?
- Did I discover a gap in their data?
- Did the user voice a new rule?

If yes, append an entry to `INSIGHTS.md`. Otherwise, leave it alone.
