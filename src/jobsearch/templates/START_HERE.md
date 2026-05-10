# START HERE

Welcome to career-hub. You have a fresh data directory. Here is the
five-minute path to your first application.

## 1. Tell your shell where your data lives

```
# bash / zsh
export JOBSEARCH_DATA_DIR=$(pwd)

# PowerShell
$env:JOBSEARCH_DATA_DIR = (Get-Location).Path
```

(Add this to your shell profile so you do not have to repeat it every
session.)

## 2. Make a profile your own

Open `profiles/PROFILE_DATA.md` (or `PROFILE_PRODUCT.md`) and replace
the placeholder skills, years, and narrative with your real data.

If you have Claude Code (or another AI assistant), open this folder in
it and say: **"interview me to fill in this profile."** The AI uses the
YAML frontmatter as a contract and asks you the right questions.

## 3. Drop a real job description in

Save the JD (or copy the text) somewhere accessible.

## 4. Run your first fit analysis

```
career-hub fit --jd /path/to/JD.docx --role data --company "Acme"
```

You will see a fit score with a breakdown of matched skills and gaps.

## 5. Generate the application

```
career-hub apply --role data --company "Acme"
```

This creates `applications/data/Acme/` with a CV copy, a cover letter,
and a fit report. Review, edit, then submit through the company's
platform (manually — career-hub never auto-submits).

Track the result:

```
career-hub log --company "Acme" --status applied
```

## What is next

- Fill in `work_experience/` with your past roles in STAR format. The AI
  uses these to write specific cover letters.
- Add certificates to `certificates/`.
- Configure `portals.yml` so the scanner discovers new openings weekly.
- Write your `personal_brand/voice_and_tone.md` so future cover letters
  sound like you.

For the AI-guided onboarding, see `CLAUDE.md` in this folder.
