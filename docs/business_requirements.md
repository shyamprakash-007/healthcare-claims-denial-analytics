# Business requirements

Audience: recruiter/interviewer and a hypothetical revenue-cycle operations stakeholder. Role: Data Analyst / BI Analyst / Healthcare Operations Analyst. Purpose: descriptive claims and denial analytics, not clinical recommendations or production healthcare work.

## Decision questions and evidence

| Business question | Implemented evidence |
| --- | --- |
| How many denied, paid and under-review claims? | Q01, Q05, Q10, Q31 |
| Which insurance types have higher denial rates? | Q11, with claim denominators |
| Which reason descriptions occur on denied claims? | Q22, Q37; Q09 is all-status frequency |
| What billed amount is associated with denied claims? | Q18, Q21, Q31 |
| How large is gross unpaid, and how does it differ from allowed gap? | Q15, Q27, financial metric definitions |
| Which procedure/diagnosis categories need review? | Q27–Q29, with no clinical-code enrichment |
| How much follow-up is required and where? | Q16, Q32, group summaries |
| What is the AR label distribution/open-status exposure? | Q07, Q33, explicit rulebook |
| How do service-date outcomes vary over time? | monthly_outcome_mix.csv, monthly_claim_status_mix.csv, Q17–Q18, Q23–Q26, with partial-September caveat |
| Where do statuses disagree? | Q30, Q34–Q36 and quality flag outputs |

## Accepted scope

Preserve the raw dataset. Audit first, freeze rules, clean, derive, explore, model in SQL, execute 30+ analyses, export a business-friendly view, reconcile results, document findings and prepare interview materials. Python runs locally and the notebook was also executed and validated in Google Colab. SQL is exercised in DuckDB and embedded PostgreSQL/PGlite; no network PostgreSQL service is installed or claimed.

## Completed Tableau scope

The user resumed Tableau work. Four dashboards, shared filters, reason selection/clear actions, native KPI checks and actual Tableau screenshots are delivered. The workbook is portable with its Hyper extract. The full package is published on [GitHub](https://github.com/shyamprakash-007/healthcare-claims-denial-analytics).

## Acceptance

One fact row per Claim ID; 1,000 input/output claims; all 15 source columns preserved; IDs/codes stay strings; no unexpected required nulls; zero-denominator handling; category validation; audit flags retained; reproducible commands; at least 30 meaningful executed queries; matching independent Python and SQL metrics; truthful limitations and synthetic disclosure. Local acceptance checks passed, including native Tableau validation. See project_status.md for the Colab execution evidence, PostgreSQL environment limitations and GitHub publication.
