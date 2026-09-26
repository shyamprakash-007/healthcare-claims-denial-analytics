# Validation report

Backend verification completed on September 22, 2026.

| Layer | Result | Evidence |
| --- | --- | --- |
| Raw preservation | SHA-256 matches original supplied file | rules.json, validation_summary.csv |
| Source audit | 1,000 rows, 15 columns, 0 missing cells, 0 duplicates, 0 invalid dates | data/audit/ |
| Amount audit | 0 negatives, 0 zeros, 0 over-billed/over-allowed relationships | data_quality_summary.csv |
| Python vs DuckDB | 62 checks passed: KPIs, all prepared fields, uniqueness, raw hash | validation_summary.csv |
| Python vs PostgreSQL | 20 KPIs passed | postgres_validation.json |
| Input boundary and engine comparison | 87 checks passed | backend_test_results.csv |
| All business analyses | 37 executed in DuckDB and PostgreSQL; all result rows match | SQL results folders |
| Notebook | All 10 code cells executed under the 11 required headings; no cell errors | 01_claims_data_preparation.ipynb |
| Google Colab runtime | September 24, 2026: 10 code cells, 62 checks passed; full analytical export matches local | colab_execution_report.json, colab_validation_summary.csv, 01_claims_data_preparation_colab.ipynb |
| Hyper extract | 5 controls passed | hyper_reconciliation.csv |
| Native Tableau | 58 KPI display comparisons passed, September 23, 2026 | tableau_native_validation.csv, screenshots |

The 87 additional checks comprise nine boundary tests, 41 view-field comparisons across engines, and 37 complete query-result comparisons. Boundaries cover missing IDs, invalid dates/numbers, unexpected categories, exact/conflicting duplicates, zero denominators, overpayments and negative amounts. Synthetic test inputs are temporary in-memory records; they are not added to the source.

Tests compare counts/categories/IDs exactly and numeric results with absolute tolerance 1e-8. All amount totals are exact to the source's whole-unit precision. One initial cross-engine check exposed unstable sorting for tied gross unpaid values; the query now includes deterministic insurance and AR tie-breakers. There was no value discrepancy.

## Native Tableau verification

58 observations cover the 19 baseline card appearances across four pages, Medicare on Executive and Financial, May, Denied status, Open AR, June 1–August 31, and the Incorrect billing information reason action. SQL expected values are computed from the analytical view; observed strings were transcribed from Tableau. Counts and whole-unit amounts match exactly. Rate displays match one decimal percentage rounding. This is not a claim that every possible filter combination was exhaustively tested.

Shared parameter state persisted between Financial and Executive. Date bounds were inclusive. Resetting filters restored the baseline; selecting a reason updated four cards and four comparison charts, and clearing it restored the page. Tooltips showed dimensions, values and metric caveats. All four pages were reviewed in maximized presentation mode, with ordered bars, complete reason labels and visible KPI amounts.

Native review exposed an internal connection assertion (C4E5AE8D) during reason selection in an earlier build. The main Hyper connection was wrapped in a named federated connection; the revised package was reopened and the action and clear operation completed without the error. The final procedure caption and ratio-band ordering were also corrected and visually checked.

The workbook was restored to the full unfiltered population. The delivered package has default All parameters and May 1–September 20 dates. The workbook is distributed as a packaged Tableau file in the GitHub repository; a separately hosted Tableau Public visualization is not included.

