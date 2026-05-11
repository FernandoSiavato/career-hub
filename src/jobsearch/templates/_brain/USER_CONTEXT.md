---
# Canonical record of who the user is.
# This file is USER-LOCKED. Never write here without explicit confirmation.
# Auto-seed from PROFILE_*.md the first time, then user confirms each field.

name: <your-name>
pronouns: <they/them|she/her|he/him>
primary_email: <you@example.com>
portfolio_url: <https://your-portfolio.example>
social_handles:
  github: <your-github>
  linkedin: <your-linkedin>

languages:
  - { code: en, level: <A1|A2|B1|B2|C1|C2|native> }
  - { code: es, level: <A1|A2|B1|B2|C1|C2|native> }

primary_role: <data | meal | product | ...>   # key from config.toml
secondary_roles: []

location: <city, country>
tz: <IANA timezone, e.g. America/Bogota>
work_modality_preference: remote   # remote | hybrid | onsite
hybrid_days_max: 2                  # only used if work_modality_preference != remote

salary_floor:
  - { currency: USD, monthly: <number> }
# Add other currencies if relevant.

sectors_target: []   # e.g. ["data platforms", "humanitarian", "AI infra"]
sectors_avoid: []    # e.g. ["adtech", "gambling"]

hard_constraints: []
# e.g. ["no relocation", "no on-call", "must support family time after 6pm local"]
---

# Who I am at work, in 200-400 words

Replace this paragraph with a short narrative the AI can quote when someone
asks "who are you" in your career-hub. Write in first person. Lead with the
problem you solve, not the title you hold. Mention the kind of company /
team that gets the best of you. Name 2-3 numbers from your real experience
so the AI never has to invent them.

End with what you will not do, and what you want next.
