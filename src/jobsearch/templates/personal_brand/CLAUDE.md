# personal_brand/ — the voice

This folder defines **who you are at work in your own words**, so the AI
writes in your voice instead of generic LLM voice. Think of it as the
style guide for cover letters, LinkedIn posts, and bio paragraphs.

## Use the question banks

Three templates live in `_template/`, each answering a different
question. Run them in this order:

1. **`brand-discovery-template.md`** — *who do I help, with what, and
   why me?* Runs the Skills × Interests × Market needs framework. Output:
   `brand_discovery.md` + a draft `brand_statement.md`.
2. **`voice-and-tone-template.md`** — *how do I sound when I write?*
   Extracts patterns from 3-5 samples of the user's own writing and
   produces prescriptive Always/Never rules in `voice_and_tone.md`.
3. **`content-strategy-template.md`** — *what do I publish and when?*
   Defines audience, pillars, cadence, and hard rules.

Run each iteratively. The voice template is the highest-leverage one for
cover letters; the discovery and strategy templates support longer-term
content work.

## Recommended files

```
personal_brand/
  brand_statement.md         # 1-2 sentences answering "what do you do?"
  voice_and_tone.md          # how you write (rules + examples)
  content_strategy.md        # what topics you publish on, optional
  positioning.md             # market context, optional
```

## brand_statement.md

```markdown
# Brand statement (Skills × Interests × Market needs)

I help [audience] do [outcome] using [skills/approach], because [why].

## Long form
3-5 sentences expanding on the line above. What you actually do, what
makes you different, who you do it for.

## Use this when
- LinkedIn headline & about section
- First paragraph of cover letters when the JD asks for "tell us about yourself"
- Conference / podcast intros
```

## voice_and_tone.md

This is the file the `/apply` skill reads to override its default writing
rules. Make it specific:

```markdown
# Voice & tone

## Always
- First person, present tense.
- Lead with one concrete number when one exists.
- Plain language. If a 14-year-old would not understand a sentence,
  rewrite it.

## Never
- Em dash characters.
- "I am passionate about", "I firmly believe", "I am someone who".
- Filler connectors: "furthermore", "additionally", "in conclusion".
- Rule-of-three lists ("creative, collaborative, and curious").
- AI-tell vocabulary: "delve", "leverage", "robust solution", "synergy".

## Tone calibration
- For NGO / mission-driven roles: warmer, more "we" framing in the body
  paragraph after the opening.
- For B2B SaaS / engineering roles: drier, more numbers, fewer adverbs.

## Example sentences I would write
> "I built the analytics stack at Acme over four months: Postgres + dbt
> + Looker, weekly funnel reports cut from three days to two hours."

## Example sentences I would never write
> "I am a passionate, results-driven analytics professional with a
> proven track record of leveraging data to drive impactful business
> outcomes."
```

## How an AI should help here

- **First time writing voice_and_tone.md:** ask the user to paste 3-5
  paragraphs they have written that they think sound like them
  (cover letters, blog posts, LinkedIn updates). Extract the patterns:
  sentence length, opening style, vocabulary range, what they avoid.
  Propose rules with **example pairs** (always X / never Y).
- **Before generating any cover letter:** load `voice_and_tone.md` and
  apply the rules. If the rules conflict with the default rules in the
  `/apply` skill, the user's file wins.
- **Updating after a cringe moment:** if the user reads a generated
  letter and says "this does not sound like me", ask which sentence
  exactly. Add it to the "never" section with a rewrite. Iteration
  beats one-shot.
