# certificates/ — certifications, courses, credentials

Store your verifiable credentials here so the AI can list them when a JD
asks for specific certifications and so you have one place to look up
expiry dates.

## File layout

One folder per certificate (or one file for short ones):

```
certificates/
  2024_aws_solutions_architect/
    certificate.pdf
    metadata.yml
  2023_google_data_analytics/
    certificate.pdf
    metadata.yml
  2022_pmp.yml             # short: just a metadata file with the credential ID
```

## metadata.yml

```yaml
title: AWS Certified Solutions Architect - Associate
issuer: Amazon Web Services
issued: 2024-03-15
expires: 2027-03-15
credential_id: AWS-SAA-12345
verify_url: https://verify.aws/...
related_skills:
  - AWS
  - cloud architecture
  - VPC
status: active           # active | expired | revoked
```

The `related_skills` field is what the AI uses to decide whether to
mention this certificate in a given application. Match it to the
`skills.aliases` lists in your profiles.

## How an AI should help here

- **Adding a new certificate:** the user drops the PDF in a new folder.
  The AI extracts the title, issuer, issue/expiry dates from the PDF
  text and proposes a `metadata.yml`. The user confirms.
- **Pre-application check:** when running `/apply`, the AI scans this
  folder and surfaces any active credentials whose `related_skills`
  intersect with the JD's must-haves. If a JD requires PMP and the
  user has it, the cover letter mentions "PMP-certified" (verbatim) and
  the CV builder script adds it under the Education / Credentials
  section.
- **Expiry warnings:** when running `career-hub report`, the AI can be
  asked to list certificates expiring in the next 90 days.

## Privacy

PDFs may contain your full legal name, credential ID, and a verifiable
URL. Default `.gitignore` does not exclude PDFs from the data dir on the
assumption it is private. Reconsider before pushing to any remote.
