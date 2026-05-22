# Scholr Student Validation Report v2

Use this report for the next real public MVP validation cycle.

Do not enter fabricated users, quotes, screenshots, scores, or retention claims.

## Current MVP Status

- Product stage: public-access MVP
- Generation mode: OpenRouter AI generation active in production
- Retrieval: semantic retrieval supported when provider/vector diagnostics are healthy
- Fallback: lexical retrieval and academic fallback preserved
- Auth: postponed until a custom-domain-ready rollout is planned
- Next infrastructure: PostgreSQL plus pgvector
- Validation status: pending real student testing

## Validation Goal

Validate whether Scholr is genuinely useful for BTech study workflows before adding more features.

Target:
- 10 to 15 BTech students
- mixed years and branches where possible
- mixed devices, including mobile and laptop
- at least one document/PDF workflow per tester if feasible

## Test Subjects

- DBMS
- Operating Systems
- DSA
- Computer Networks
- Engineering Maths
- PYQ PDFs
- research papers
- class notes or lab manuals

## Modules To Test

- Landing page comprehension
- Dashboard navigation
- Research
- Notes
- Doubt
- Documents upload
- Document answer with citations
- Mobile flow
- Desktop flow
- Provider/fallback messaging clarity

## Session Tracker

| Session | Date | Student Type | Device | Subject | Module / Workflow | Prompt / Task Summary | Usefulness (1-5) | Citation Usefulness (1-5 / NA) | Confusion Point | Hallucination / Unsupported Claim? | Would Use Before Exam? | Issues Found | Fixes Shipped |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 2 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 3 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 4 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 5 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 6 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 7 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 8 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 9 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 10 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 11 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 12 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 13 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 14 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| 15 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Academic Task Bank

Use these as starting prompts. Replace them with real course-specific prompts when students provide better ones.

| Subject | Suggested Task |
| --- | --- |
| DBMS | Generate notes on normalization and ask a doubt about 3NF vs BCNF. |
| Operating Systems | Explain deadlock prevention vs avoidance with an exam-style answer. |
| DSA | Create revision notes for graph traversal and ask for viva questions. |
| Computer Networks | Explain TCP congestion control and extract important questions. |
| Engineering Maths | Summarize Laplace transforms or eigenvalues for quick revision. |
| PYQ PDF | Upload a PYQ set and identify repeated topics without fake probability claims. |
| Research paper | Upload a paper and ask for contributions, limitations, and citations. |

## Quantitative Summary

Fill only after real testing.

| Metric | Value |
| --- | --- |
| Testers completed | TBD |
| Average usefulness score | TBD |
| Students who would use before exams | TBD |
| Students who preferred mobile | TBD |
| Students who used Documents | TBD |
| Citation usefulness average | TBD |
| Reported hallucinations | TBD |
| Top confusion point | TBD |
| Top requested improvement | TBD |

## Anonymized Quote Bank

Record only real quotes, anonymized and with consent where appropriate.

- TBD

## Issues Found And Fixes Shipped

| Date | Issue Found | Severity | Module | Fix Shipped | Verification Status |
| --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD |

## Notes For Reviewers

- This report is a template until real student sessions are completed.
- Physical-device iPhone testing should be explicitly marked as physical-device testing.
- Viewport emulation is useful for layout checks, but it is not the same as physical Safari validation.
