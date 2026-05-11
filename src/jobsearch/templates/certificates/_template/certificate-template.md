# Certificate Documentation Template

> **For the AI:** This template documents one credential (course,
> certification, training, license, scholarship). The output is a
> `certificates/<slug>/` folder with a `metadata.yml`, the original PDF
> (when available), and a one-paragraph `notes.md`. Run iteratively, but
> certificates usually fit one session each.
>
> **Before asking:**
> 1. If the user pastes a PDF or a credential URL, extract issuer, dates,
>    credential ID, and any visible skills automatically.
> 2. Reconcile the certificate's covered skills with
>    `profiles/PROFILE_<ROLE>.md` — note which profile skills this cert
>    proves. The fit_analyzer can use this later.
> 3. Skip questions whose answers are already on the PDF.

---

## 1 — Document intake

- **PDF path or credential URL**:
- **Local copy stored at** (default: `certificates/<slug>/credential.pdf`):
- **Verify URL** (e.g. Coursera / LinkedIn Learning / Credly badge):

## 2 — Metadata

For each cert capture:

- **Title** (as printed on the certificate):
- **Issuer** (e.g. Coursera + partner university; AWS; Anthropic; your
  employer):
- **Issued date** (YYYY-MM-DD):
- **Expiry date** if any (YYYY-MM-DD or `none`):
- **Credential ID** (often visible on the PDF):
- **Hours / CEU / ECTS** if disclosed:
- **Skills proven** (3-8 items, names matching `PROFILE_*.md::skills[].name`
  so the fit_analyzer can connect them):
- **Notable detail**: a one-line reason this cert matters
  (e.g. "Capstone project graded by Stanford instructor; cited by Coursera
  as top 1%"):

## 3 — Renewal plan

- **Renewal needed**: yes / no / unsure
- **If yes: by when** (YYYY-MM-DD):
- **Renewal cost / effort estimate**:
- **Decision rule** (e.g. "renew only if I am still targeting cloud roles
  by 2027"):

## Output rules

Write `certificates/<slug>/metadata.yml`:

```yaml
title: <§2 Title>
issuer: <§2 Issuer>
issued: <§2 Issued>
expiry: <§2 Expiry>
credential_id: <§2 ID>
hours: <§2 Hours>
verify_url: <§1 Verify URL>
skills_proven: [<§2 list>]
related_profile_skills: [<names from PROFILE matching §2 skills>]
notable: <§2 Notable detail>
renewal:
  needed: <§3>
  by: <§3 date>
  decision_rule: <§3>
```

And a sibling `notes.md` with one paragraph (~80 words) describing what
the credential covered. The AI uses both files when answering "do you have
a cert for X?" and when building cover letters that name credentials.

If the original PDF is available, copy it to
`certificates/<slug>/credential.pdf`. If not, link to it from `verify_url`.

Never claim a skill the credential did not cover. If `§2.skills_proven`
is unclear, leave it `[]` and ask the user in a follow-up session.
