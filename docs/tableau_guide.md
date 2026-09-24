# Tableau dashboard guide

Open `tableau/Healthcare_Claims_Denial_Analytics.twbx` in Tableau Public/Desktop. It packages the workbook and 1,000-row, 41-field Hyper extract from `vw_claims_analytics`. No live database or credentials are required. Select **01 Executive Overview** at the bottom to begin; the generated workbook may initially show the AR page. Maximize Tableau and use F7 for presentation mode; F7 returns to editing.

| Page | Purpose |
| --- | --- |
| Executive Overview | Six KPI cards, monthly volume, status mix, insurance comparison and outcomes |
| Denial Analytics | Four KPI cards, reason counts, insurance rates, monthly trend and procedure exposure |
| Financial Performance | Five KPI cards, monthly billed/allowed/paid panels, payment rate, unpaid procedures and ratio bands |
| AR and Data Quality | Four KPI cards, AR labels, follow-up comparisons, status/outcome matrix and review trend |

## Controls and interpretation

- From and Through are inclusive service-date bounds. The native date picker uses the computer's locale; validation used May 1 through September 20, 2024.
- Insurance, Status, AR status and Month are single-selection parameters with All options. All six parameters combine with AND and affect every page. Month is YYYY-MM. An incompatible selection can produce an empty population; undefined ratios are blank.
- Click a bar in Denials by reason to filter the other eight views on that page. The denial-rate denominator becomes all claims carrying that reason in the current parameter population. Click empty space in that chart to clear the selection. Reset categorical parameters to All and dates to the full interval for the baseline.
- Hover over marks for values, dimensions and metric explanations. Avoid Keep Only/Exclude in the tooltip during a simple walkthrough because these create additional filters.
- Counts use distinct Claim IDs. Payment rate is total paid divided by total billed. Any denial billed includes status OR outcome denials once. Gross unpaid is billed minus paid; it is not proven recoverable AR.
- Monthly financial panels use separate value axes: compare their numbers, not line heights across panels. September includes only days 1–20. Percentage bands are half-open intervals; unobserved bands do not appear.
- Orange identifies denial analysis, teal general workload, green payments; the matrix uses intensity plus numeric labels. Source reason descriptions and procedure codes are retained without invented meanings.

## Rebuild and evidence

After regenerating the analytical CSV, run `python scripts/build_tableau.py`. This recreates the TWB, Hyper and TWBX. Keep `Data/claims.hyper` next to the unpackaged TWB. Prefer the TWBX for portability. Recheck the dashboards after changing source data or calculations.

The four PNGs under screenshots are actual Tableau presentation captures. Native KPI comparisons are in `data/exports/tableau_native_validation.csv`; representative filter/action captures are in `docs/validation_evidence`. These are observed UI checks, separate from the five Hyper data controls.

The delivered files are local. In this Tableau installation Ctrl+S invoked a publishing flow; it was cancelled. Use a clearly labelled local-save menu if saving edits and review any publishing destination before proceeding.
