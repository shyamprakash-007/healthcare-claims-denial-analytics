# Project status

**Project complete and published September 24, 2026.** The user resumed the earlier Tableau hold. The full package contains the verified dashboards and backend.

| Workflow sections | Status and evidence |
| --- | --- |
| 0–3 Purpose, contract, architecture | README, business requirements, preserved raw source |
| 4–7 Audit, cleaning, derived metrics, definitions | Executed notebook, audit files, rulebook, metric definitions |
| 8–10 SQL model, analyses, analytical view | Seven dimensions, claim fact, six SQL scripts, 37 analyses executed in two engines |
| 11–12 Tableau and UX | Four dashboards, 34 worksheets, six shared parameters, reason filter actions, metric tooltips, screenshots |
| 13–15 Insights, RCM questions, integrity | Twelve evidence-based insights and explicit synthetic-data limitations |
| 16 Notebook | All eleven specified headings and ten code cells executed locally and in Google Colab |
| 17 Validation | Python, DuckDB, PostgreSQL, Hyper and native Tableau reports |
| 18 Documentation | README, dictionary, rules, requirements, insights, limitations, dashboard guide |
| 19–20 Resume and interview | Four resume bullets; ten SQL, ten analytics and five Tableau answers; two explanations |
| 21 Enhancements | Optional future work documented; no invented enrichment added |
| 22–26 Delivery and integrity | Public GitHub repository, full local ZIP, file hashes, screenshots and reproducible scripts |

## Cloud execution, publication and environment limitations

- Google Colab execution completed September 24, 2026 on Python 3.13.15: 10 code cells, 62 passing checks, and all 1,000 rows / 41 analytical fields match the local export. The executed cloud notebook and runtime report are included.
- SQL was executed in DuckDB and real PostgreSQL 18.3 through embedded PGlite. A separate network PostgreSQL deployment was not exercised.
- The complete project is published at [https://github.com/shyamprakash-007/healthcare-claims-denial-analytics](https://github.com/shyamprakash-007/healthcare-claims-denial-analytics). The packaged Tableau workbook and dashboard screenshots are included in the repository and local ZIP. A separately hosted Tableau Public visualization is not part of this delivery.
- Tableau native checks used Public 2026.2 on Windows. Mobile layouts, screen-reader accessibility and older Tableau versions were not formally certified.
