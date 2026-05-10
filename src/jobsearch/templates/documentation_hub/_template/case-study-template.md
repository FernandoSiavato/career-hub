# Project Case Study Template

> **For the AI:** This template is filled in iteratively, not all at once.
> When the user runs `/apply` or asks for help documenting a project, treat
> this file as a structured interview. Do NOT just dump the questions and
> ask the user to fill them all. Instead:
>
> 1. **Read what the user already has** (notes, repo READMEs, work_experience
>    entries, old presentations). Pre-fill as many answers as you can.
> 2. **Ask only the questions where the answer is missing or shallow.** Start
>    with the highest-leverage gaps: problem framing, decisions and trade-offs,
>    quantified results.
> 3. **Probe.** If an answer is vague ("system was slow", "users were happy"),
>    ask for the specific number, the specific person, the specific incident.
> 4. **Suggest architecture or diagrams** when the user describes a system but
>    has not drawn it. Offer to sketch a mermaid diagram or component diagram
>    from their description.
> 5. **Never invent metrics, dates or stack details.** Mark unknown answers as
>    `?` and revisit them later.
>
> When ~80% of the sections are filled, generate a polished 400-700 word case
> study using the rules in the "Output rules" section at the bottom.

---

## 1 — Project context

Goal: place the reader in the real world of the project before talking tech.

- **Name of the project:**
- **Where it happened** (employer, client, OSS, side project):
- **Your specific role** (`single backend dev`, `led team of 3`, `architected and mentored juniors`):
- **Period** (`mm/yyyy – mm/yyyy`):
- **How many people were affected** (`5,000 active users`, `50 internal employees`, `8-dev team`):

## 2 — The real problem

Goal: prove you started from understanding a problem, not from picking tools.

- **What was the core problem before you started?**
  *Be specific. Avoid "the system was slow". Instead: "billing failures couldn't be diagnosed without reading raw logs manually".*
- **Who suffered the problem and how did it show up in their day-to-day?**
- **Cost of inaction** (time, money, lost users, risk):
- **Prior workaround and why it wasn't enough:**
- **How you validated this was the right problem to solve:**

## 3 — Decisions and trade-offs

Goal: show your decisions had reasoning, not fashion.

- **Options you evaluated** (list at least 2-3 alternatives, even if shallow):
- **What you chose and why over the others** (connect to constraints: cost, time, team, scale):
- **Top 2-3 design decisions.** For each: *What did you decide? Why? What trade-off did you accept?*
  - Decision 1:
  - Decision 2:
  - Decision 3 (optional):
- **Real constraints that shaped the decisions** (budget, time, tech debt, team):
- **Something you wanted to do but couldn't, and why:**

## 4 — Stack and architecture

Goal: give the reader technical context without burying them. Tech is evidence, not the point.

- **Main technologies:** languages, frameworks, databases, cloud, observability, tooling.
- **One piece of the stack worth highlighting** ("we chose Kafka over RabbitMQ because we needed retention for audits"):
- **Architecture in 2-3 plain sentences** (as if explaining to a non-engineer):
- **Diagram** (path to image, mermaid block, or "pending"):

## 5 — Process and execution

Goal: show how you think and work, not just what you built.

- **Process from problem to solution** (phases, iterations, pivots — pivots are valuable):
- **Toughest technical obstacle:**
- **How you solved it:**
- **Solo vs team** (and how you led or coordinated if applicable):
- **One non-technical lesson** (communication, prioritization, expectations):

## 6 — Results and impact

Goal: connect technical work to real value. This is the section that most differentiates senior profiles.

- **What concretely changed after your solution** (before vs after, observable):
- **Quantified metrics** (`incident resolution: 3h → 18min`, `prod errors: -40%`):
- **Business or user impact** (`X hours saved per week`, `Y% higher satisfaction`):
- **Qualitative results** (team feedback, client quotes, cultural shift) or `N/A`:

## 7 — Reflection

Goal: show you learn and evolve, not just execute.

- **What you would do differently if starting today:**
- **What you learned technically that you didn't know before:**
- **What you took away about judgment, decision-making, systems thinking:**

## 8 — Links and evidence

- **Repository** (URL or `private/confidential`):
- **Live product or demo** (URL or `N/A`):
- **Screenshots, videos, GIFs** (paths or URLs — include main screen, key flow, dashboard if relevant):
- **Articles, posts or talks where you explained this** (URL or `N/A`):
- **Testimonials or feedback you can quote** (direct quote or paraphrase with context):

## 9 — Portfolio metadata

- **Primary category** (Infrastructure / Product / Data / Mobile / Frontend / Backend / Full Stack / DevOps / ML):
- **Tech tags** (max 6, e.g. `Node.js, PostgreSQL, Kafka, AWS, Observability, Microservices`):
- **Soft-skill tags this project demonstrates** (e.g. `decisions under uncertainty, technical communication, leadership, system design`):
- **Who this would convince** (e.g. `scaling startups`, `companies with legacy systems`, `teams improving observability`):
- **One-sentence summary** (e.g. *"Designed a distributed tracing system that cut incident resolution time by 80%."*):

---

## Output rules — how the AI should write the final case study

When the answers above are ~80% complete, generate a case study following these rules:

1. **Open with the problem**, not the technology. The first sentence must capture the real pain.
2. **Narrative arc:** Context → Problem → Exploration → Decision → Execution → Impact → Reflection.
3. **Every tech decision must carry its "why".** Never mention a tool without explaining what problem picking it solved.
4. **Results must connect technical metric to business value.** Not just *"latency -40ms"* — what did that mean for the user or team?
5. **Preserve the author's voice.** If there are direct quotes in the answers, use them verbatim. Do not smooth them out.
6. **Never invent metrics, dates or stack details.** If something is `?` or `N/A`, omit it or call out the gap.
7. **Length:** 400-700 words for the portfolio summary; optionally expandable to 1,200-1,500 for the full case study.
8. **Format:** structured markdown, ready to paste into Notion, a portfolio site, or LinkedIn.
