# Content Strategy Template

> **For the AI:** This template captures the user's editorial plan: who
> they write for, what themes (pillars), what formats, what cadence, what
> hard rules. The output is `personal_brand/content_strategy.md`. Run
> iteratively.
>
> **Before asking:**
> 1. Read `personal_brand/brand_discovery.md` and `voice_and_tone.md` —
>    most of the audience and voice work is already done.
> 2. Read `documentation_hub/` — case studies are content gold.
> 3. Read `_brain/USER_CONTEXT.md.languages` — bilingual users may need
>    pillars and cadence per language.

---

## 1 — Audience

Goal: who do you publish for, today, with intention.

- **Primary audience** (one specific persona — name a fake "Maria the data
  manager at a Series A startup" or "Pedro the M&E coordinator at a
  WV-style INGO"):
- **Secondary audience** (the people who refer the primary):
- **Aspirational audience** (where the user wants to be invited in two
  years — interview them implicitly with each post):
- **Why these and not others**: 2-3 sentences. This filters every future
  topic.

## 2 — Content pillars

Goal: 3-5 mutually exclusive themes. Every post belongs to one.

For each pillar:
- **Name** (e.g. "system case studies", "stack decisions explained",
  "indicator design field notes"):
- **What it answers** for the reader:
- **Evidence the user has** (which case studies in `documentation_hub/`,
  which work_experience entries supply material):
- **Format** that fits the pillar (post + image, thread, long-form
  Substack, short video):

> If two pillars overlap, the user does not have pillars — they have one
> pillar with two names. Force the choice.

## 3 — Cadence and distribution

Goal: a realistic weekly rhythm the user can sustain.

- **Posts per week** (be honest — fewer that ship beats more that don't):
- **Distribution across pillars** (e.g. 35% case studies, 25% stack, 25%
  field notes, 15% build-in-public):
- **Comment cadence** (1 long comment per weekday on others' posts is a
  high-leverage habit — does the user commit?):
- **Public artifact cadence** (every N weeks, ship a visible technical
  artifact — repo, demo, write-up — so the brand has receipts):
- **Languages**: per-pillar or split (e.g. case studies in ES, stack
  decisions in EN)?

## 4 — Hard rules (no negotiation)

These are publication-stoppers. The AI never bypasses them.

- **Language rule**: always in <ES|EN|both>?
- **Person rule**: always first person?
- **Voice rules** (inherited from `voice_and_tone.md` Always/Never).
- **Topic exclusions** (e.g. "no current employer specifics", "no client
  names without permission", "no salary numbers"):
- **Evidence rule**: every post must include at least <X> concrete number
  or specific company / project name. Vague essays are rejected.
- **Format constraints** (e.g. "no Canva templates", "no all-caps
  headings", "no emojis in long-form").

## Output rules

Write `personal_brand/content_strategy.md`:

```markdown
# Content strategy

## Audience
- Primary: <§1>
- Secondary: <§1>
- Aspirational: <§1>

## Pillars
1. <§2 name 1> — answers: <what>; evidence: <docs>; format: <how>
2. <§2 name 2>
3. <§2 name 3>
(up to 5)

## Cadence
- Posts/week: <§3>
- Distribution: <§3 percentages>
- Comments/day: <§3>
- Artifacts: <§3>
- Languages: <§3>

## Hard rules
- <§4 bullets>

## Pipeline integration
- Sparks live in: `personal_brand/sparks/<YYYY-MM-DD>_<slug>.md`
- Drafts live in: `personal_brand/drafts/<slug>.md`
- Published archive lives in: `personal_brand/published/<slug>/`
```

When the user asks the AI to write, edit or schedule content, the AI
applies §4 (hard rules) without exception and uses §2 (pillars) to filter
which spark to develop next.
