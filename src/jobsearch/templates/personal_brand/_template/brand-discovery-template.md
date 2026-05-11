# Brand Discovery Template

> **For the AI:** This template runs the *Skills × Interests × Market needs*
> framework to find the user's brand intersection. The output is
> `personal_brand/brand_discovery.md` and a draft `brand_statement.md`. Run
> iteratively; the user does not need to be ready to publish — they need to
> see the intersection clearly.
>
> **Before asking:**
> 1. Read `profiles/PROFILE_*.md` for skills + positioning.
> 2. Read `work_experience/` for what the user has actually done.
> 3. Read `documentation_hub/` for projects the user is proud of.
> 4. Read `_brain/USER_CONTEXT.md` for declared sectors and constraints.
> 5. Show the intersection back to the user as a starting hypothesis, then
>    invite them to refine. People recognize their brand faster than they
>    describe it cold.

---

## 1 — Skills (what you are credibly good at)

Goal: 5-8 skills that survive both *I can do this* and *people pay me to do
this*.

- **List skills where you have ≥3 years of paid practice**:
- **List skills where you have public evidence** (repos, docs, talks,
  shipped products, certifications):
- **List skills where you are recognized internally but have not made
  public** — these are candidates for content / portfolio work.
- **Anti-list**: things you are technically able to do but no longer want
  to lead with (this matters as much as the positive list).

## 2 — Interests (what energizes you on a Wednesday at 3pm)

Goal: 3-5 themes that make you read, build, write voluntarily.

- **What do you read about in your downtime** (last 5 newsletters, last 5
  YouTube channels, last 3 books)?
- **What problem do you keep returning to** across jobs, even when nobody
  asked you to?
- **What kind of company / team / role would you join at 80% of your
  current salary** because the work itself is the payoff?
- **What kind of work do you turn down** even when paid well?

## 3 — Market needs (who pays for the overlap)

Goal: 2-3 audiences where Skills × Interests intersects a real budget.

- **Companies / sectors actively hiring for the intersection**: list
  specific employer types and 3-5 example companies for each.
- **Buyers' pain language**: how do hiring managers describe this problem
  in their own words (LinkedIn searches, JDs, conference talks)?
- **Salary band the market signals**: low / mid / high for the
  intersection. (Sanity check the user's `salary_floor`.)
- **What you are NOT** even if it pays more: positions that look adjacent
  but pull you away from the intersection.

## 4 — Brand statement synthesis

Goal: a one-sentence positioning + a paragraph version.

- **Short form** (≤25 words). Format suggestion:
  > "I help <audience> do <outcome> using <unique combination>, especially
  > when <constraint that filters out generalists>."
- **Long form** (~80 words). Should include:
  - The intersection from §1 + §2
  - The audience from §3
  - 1-2 concrete numbers from `work_experience/`
  - What you refuse to do (from §1 anti-list)
- **Mother rule** — one sentence to filter every future bio / post / talk:
  *"If a piece of content does not strengthen the short-form statement, it
  does not ship."*

## Output rules

Write `personal_brand/brand_discovery.md`:

```markdown
# Brand discovery

## Skills (top 5-8, evidenced)
- <§1 list>

## Anti-list (skills no longer leading with)
- <§1 anti-list>

## Interests
- <§2 themes>

## Market needs
### Primary audience: <§3>
### Secondary audience: <§3>

## The intersection
<2-3 sentence narrative describing where §1, §2, §3 overlap>

## Brand statement (short)
"<§4 short form>"

## Brand statement (long)
<§4 long form>

## Mother rule
<§4 mother rule>
```

Also write a draft `personal_brand/brand_statement.md` containing **only**
the short form + long form, so the AI can quote it without reading the
whole discovery doc.

If the user is not sure about an answer, leave `?` and revisit. Brand
clarity comes in iterations.
