# profiles/ — the epicenter

This is the most important folder in career-hub. Every `PROFILE_<ROLE>.md`
is the single document the CLI and the `/apply` skill consult when scoring
a JD and writing applications. The YAML frontmatter is the contract; the
markdown body below it is your narrative.

## Use the question bank

When the user asks "interview me for my data profile" or "let's refresh
my MEAL profile", open **`_template/profile-interview-template.md`** and
run it iteratively:

1. Read `_brain/USER_CONTEXT.md`, `work_experience/`, and any existing
   `PROFILE_*.md` first. Pre-fill every section you can from those
   sources.
2. Show the user what you already have before asking new questions.
3. Ask only the questions whose answer is missing or shallow.
4. Probe vague answers — "comfortable with SQL" needs a follow-up about
   window functions, query tuning, table size.
5. Never invent skills, years, KPIs or aliases.
6. Save progress after every section so the user can stop and resume.

## File layout

```yaml
---
id: data                    # role key (must match a role in config.toml)
name: Your Name
role_title: Data Analyst    # title that appears in CV header
language: en
secondary_language: es
english_level: 5            # 1-5

total_years_experience: 4

template_map:
  en: "cvs/CV_DATA.docx"
  es: "cvs/CV_DATA_ES.docx"

keywords:                   # 8-12 terms that should appear in CV/letter
  - SQL
  - Python
  - ...

skills:                     # the source of truth for fit analysis
  - name: SQL
    category: technical     # technical | tool | soft | language
    level: 4                # 1-5 self-rated
    years: 4
    aliases:                # synonyms for fuzzy matching
      - postgresql
      - bigquery
---

# Narrative
A short paragraph in your own voice. Concrete numbers, no filler.
```

## How an AI should help you fill this

If the user asks you (the AI) to fill in a profile, do this:

1. Read the file as it stands and identify which fields are placeholders.
2. **Interview, do not invent.** Ask the user about their last 2-3 roles,
   what tools they used daily, what level they consider themselves at, and
   what kind of work they want to do next. One question at a time.
3. Translate answers into the YAML schema above. For `level`, map 1=heard
   of it, 3=use comfortably, 5=could teach it.
4. For `aliases`, propose 3-5 synonyms that recruiters actually use in JDs
   for that skill, in both languages if relevant.
5. The narrative paragraph at the bottom should be **specific**: lead with
   one quantified result, not adjectives.

## Common mistakes to avoid

- Listing 30 skills. Pick the 8-15 you would actually want to be tested on.
- Vague aliases (`scripting` matches everything). Use concrete tool names.
- Years that do not add up to `total_years_experience`. If you have used
  Python for 3 years inside 4 years of total experience, that is fine —
  just keep it consistent.
- Skipping the narrative. The `/apply` skill uses it to set the voice of
  the cover letter.

## After editing

You do not need to restart anything. The CLI reads the file fresh on every
invocation. Run a quick sanity check:

```
career-hub fit --jd <some-real-JD.docx> --role data --company "Test"
```

A reasonable JD should produce a fit score above 50% and matched skills
that you recognize.
