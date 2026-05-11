# Voice & Tone Template

> **For the AI:** This template captures the user's writing voice so every
> cover letter, post and bio sounds like them. The output is
> `personal_brand/voice_and_tone.md` — a prescriptive doc with always /
> never rules and example pairs. Run iteratively.
>
> **Before asking:**
> 1. Read `personal_brand/brand_discovery.md` for positioning.
> 2. If the user has paste-able writing samples (LinkedIn posts, old cover
>    letters, blog drafts), get them first — extracting patterns from real
>    samples is faster than describing voice abstractly.
> 3. Save partial progress so the user can return.

---

## 1 — Writing samples intake

Goal: 3-5 paragraphs of the user's own writing the AI can pattern-match.

- **Paste samples here** (rough is fine — drafts beat polished if drafts
  show how the user thinks):
  - Sample 1:
  - Sample 2:
  - Sample 3:
- **Sample type** for each (cover letter / LinkedIn post / blog / email
  to a colleague):
- **Self-rating** for each (would publish / would edit heavily / would
  delete) — tells the AI which patterns to amplify vs avoid.

## 2 — Pattern extraction

The AI reads the samples and surfaces patterns. The user confirms or
corrects.

- **Sentence length**: short staccato / medium balanced / long unfolding?
  Show the average word count of sentences in samples §1.
- **Openers**: do they start with the problem, with the person, with the
  number, with a question?
- **Vocabulary register**: technical-pragmatic, warm-NGO, dry-academic,
  founder-direct, hybrid?
- **Recurring devices**: lists of three, em dashes, parentheticals, direct
  quotes from colleagues, before/after numbers, etc.
- **Concrete verbs the user actually uses** (extract from §1):
- **Adjectives the user avoids** (e.g. *innovative*, *passionate*,
  *holistic*) — list them as future no-ship words.

## 3 — Always / Never rules (the prescriptive layer)

This is the part the AI quotes when editing the user's writing.

**Always:**
- Always write in <first person | third person>.
- Always lead with <a number | a person | the problem>.
- Always include at least <X> concrete number per paragraph.
- Always end paragraphs on <a verb | a question | a contrast>.
- (Add user-specific rules)

**Never:**
- Never use these words: <list from §2 avoid>.
- Never use em dash (`—`). Use commas or periods.
- Never use buzzwords: `synergy`, `holistic`, `paradigm`, `cutting-edge`,
  `passionate`, `thrilled`, `seamless`, `robust`, `dynamic`, `innovative`,
  `disruptive`, `transformative`.
- Never use rule of three with the conjunction "and" (e.g. "X, Y and Z").
  Rewrite as "X and Y, plus Z".
- Never use negative parallelism ("not only X but also Y").
- (Add user-specific rules)

## 4 — Tone calibration by audience

The user's voice can shift register without losing identity. Map who
hears each tone:

- **Audience A** (e.g. NGO hiring manager): tone is warm-professional,
  lead with mission alignment, quote donors and beneficiaries.
- **Audience B** (e.g. B2B engineering manager): tone is technical-direct,
  lead with the system shipped and the numbers behind it.
- **Audience C** (e.g. founder DM): tone is peer-conversational, short
  sentences, "I" and "you" addressed.
- **Audience D** (e.g. LinkedIn public post): tone is build-in-public,
  story-first, single-idea per post.

For each audience: 1-2 hooks that work and 1-2 hooks that do not.

## Output rules

Write `personal_brand/voice_and_tone.md`:

```markdown
# Voice & tone

## Central voice
<2-3 lines summarizing §2 — who the user sounds like, what they avoid>

## Always
<bullets from §3 Always>

## Never
<bullets from §3 Never>

## By audience

### NGO hiring manager
- Hooks that work: <§4>
- Hooks that fail: <§4>

### B2B engineering manager
- Hooks that work: <§4>
- Hooks that fail: <§4>

### (other audiences §4)

## Voice anchor sample
<the single best paragraph from §1 — the AI uses it as the verbatim style
guide when generating new content>

## Mother rule
Every piece of writing must leave the reader with one clear impression of
who the author is. If a paragraph could be written by anyone in the same
role, rewrite it.
```

When the user later asks the AI to draft or review writing, the AI quotes
the Always / Never sections and the voice anchor — that is what makes the
output sound like them, not generic.
