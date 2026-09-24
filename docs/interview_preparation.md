# Interview preparation

Answers describe the completed local analytics project and native-verified Tableau workbook. Execution and publication exceptions are documented in project_status.md.

## SQL: 10 questions

### 1. Why normalize this flat source?

To make dimension vocabularies and keys explicit, prevent accidental text inconsistency in joins, and separate claim-level facts from descriptive attributes. Provider and patient dimensions add little compression here because each ID is unique.

### 2. Why a star schema?

The claim is the analytical grain; date, insurance, reason, procedure, diagnosis, provider and patient are dimensions used to filter and group those facts.

### 3. When did you use CTEs instead of subqueries?

CTEs make monthly aggregates followed by LAG readable in Q23–Q26. Q29 isolates the percentile threshold in a CTE and cross joins it to denied claims.

### 4. How is denial rate calculated?

Distinct claims with Claim Status Denied divided by distinct claims in scope. Outcome denial rate is separate. The unfiltered values are 32.8% and 33.1%.

### 5. How is MoM change calculated?

Aggregate by service_month_start, use LAG for the prior observed month, then (current-prior)/NULLIF(prior,0). The first month is null and September is explicitly partial.

### 6. Where are window functions used?

RANK in Q21, DENSE_RANK in Q22, LAG in Q23–Q25, cumulative SUM in Q26, and ROW_NUMBER in Q29 and Q37.

### 7. How are zero denominators handled?

NULLIF in SQL and masked denominators in Pandas return null for undefined ratios. The boundary test verifies zeros are not silently turned into a zero rate.

### 8. How did you validate the engines?

All 37 query results match across DuckDB and embedded PostgreSQL. Twenty headline KPIs also match Python; all row-level analytical fields are compared.

### 9. How is double counting prevented?

Claim ID is unique in the fact, dimension values are unique, foreign keys enforce valid joins, and the final view is reconciled at the same claim grain.

### 10. Why not average claim payment ratios?

A simple average weights small and large claims equally. The portfolio payment rate uses total paid / total billed and is 67.5505%.

## Analytics: 10 questions

### 1. What is the most useful primary KPI?

Claim Status Denial Rate summarizes the operational source label, but it is always accompanied by Outcome Denial Rate and quality caveats.

### 2. What did reason analysis show?

Incorrect billing information and Authorization not obtained account for 97 of 328 denied claims, or 29.57%. They are source descriptions, not proven causes.

### 3. Why keep denial and outcome separate?

Only 112 claims are denied in both fields despite nearly equal headline rates. The union is 547, and each definition answers a different question.

### 4. Why flag inconsistencies?

Without dates or lifecycle definitions, selecting a single authoritative status would fabricate certainty. The project preserves labels and documents review rules.

### 5. What limits the financial analysis?

Currency, contractual adjustments and collection events are absent. Gross unpaid cannot be asserted to be collectible AR or denied billed value to be lost revenue.

### 6. Which category has the highest denial rate versus amount?

Medicare has the highest observed rate at 36.05%; Commercial has the largest denied billed amount at 27,386 source units.

### 7. What did follow-up analysis show?

522 claims require follow-up, including 181 Paid-status claims. A denied-only queue would omit 358 required follow-ups.

### 8. How would you interpret September?

Only through September 20 is present. I label it partial and avoid claiming that the raw -33.84% volume change from August indicates deterioration.

### 9. Why avoid provider rankings?

There is only one observation for each provider, giving unstable 0% or 100% denial rates and no repeat history.

### 10. What evidence would be needed for operational recommendations?

Validated lifecycle definitions, submission/payment/adjustment dates, contracts and repeat observations. The current actions are investigation proposals, not proven improvements.

## Tableau: 5 questions

### 1. Why did you select each chart?

Bars compare category counts or financial amounts; lines show service-month patterns. The status/outcome matrix reveals conflicting combinations. Separate monthly financial panels avoid dual axes, with numeric axes kept visible. Four pages separate executive, denial, financial and follow-up questions.

### 2. Which filters affect KPI denominators?

The inclusive date range, insurance, status, AR and month parameters form one AND condition applied across all sheets. Denial rate uses distinct denied claims divided by all distinct claims in that selected population. Payment rate uses the ratio of sums, not the average claim ratio.

### 3. How does reason selection work?

Selecting a bar filters eight target views on the denial page. For Incorrect billing information, the page shows 49 denied claims, 34.5% denial rate, 15,261 denied billed and 26,405 any-denial billed units. Clicking empty chart space clears it. The source reason chart stays available for another selection.

### 4. How did you reconcile Tableau to SQL?

I compared all baseline KPI cards and selected insurance, month, claim-status, AR, date-range and reason populations against independent SQL queries. Counts and amounts match exactly; rates match their one-decimal display. Hyper-level controls and native screenshots provide separate evidence.

### 5. How did you check the presentation?

I opened the packaged workbook in Tableau, reviewed all four pages in presentation mode, tested controls and tooltips, corrected truncated financial totals, widened reason labels and ordered ratio bands. Numeric labels supplement color. This was a visual usability review, not formal screen-reader or accessibility certification.

## Two-minute project explanation

I built a Healthcare Claims and Denial Performance Analytics portfolio project using 1,000 synthetic claims. The goal was to answer operational questions about denials, financial gaps, follow-up and reporting quality.

I started with an audit of all 15 fields, preserving IDs as text so leading zeros were not lost. There were no missing values or duplicate claim IDs, but the status fields needed careful interpretation. I froze explicit quality rules and retained every claim. I kept operational denial, outcome denial and their union separate. The headline rates were 32.8% and 33.1%, but only 112 claims overlapped.

I built a star schema with seven dimensions, a claim-level fact and analytical views. I wrote 37 SQL analyses using conditional aggregation, CTEs, ranking, LAG and percentile logic. I executed them in DuckDB and embedded PostgreSQL and verified that every query result matched. Twenty headline KPIs also reconcile with Python.

A key finding was that every denied claim still carried a payment. Therefore, I described the 98,069 billed units associated with denied claims as exposure, not lost revenue. Similarly, the overall 96,437 gross unpaid units are not proven collectible AR. The code, executed notebook, query outputs and rulebook make these conclusions reproducible. Four interactive Tableau dashboards show the executive picture, denial patterns, financial gaps and follow-up quality. I checked the cards and selected filter populations against SQL and delivered a portable workbook with screenshots.

## Thirty-second resume explanation

I prepared and modeled 1,000 synthetic healthcare claims, built 37 SQL analyses, and reconciled the results across Python, DuckDB and PostgreSQL. The work focused on denials, follow-up and financial gaps, with explicit quality rules for conflicting status labels. I avoided interpreting gross unpaid as collectible AR and documented the limitations. Four verified Tableau dashboards make these results interactive. This is a synthetic portfolio project delivered as a reproducible local package.
