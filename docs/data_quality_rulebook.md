# Frozen data-quality rulebook

Rule version: 1.0. Frozen after the source audit, before cleaning and metric engineering. The vocabulary is in `rules.json`. It describes observed synthetic data, not an authoritative healthcare code set.

## Grain and required values

One source row represents one claim in this snapshot. All 15 source fields are required for this specific reproducible build. Empty strings/whitespace become null. Invalid numbers/dates become null and fail the build. New category values fail validation pending review. This avoids silently dropping records from headline denominators. There are no nulls, invalid dates, or duplicate claims in the delivered source.

Preserve `data/raw/claim_data.csv` byte-for-byte. The SHA-256 is recorded in `rules.json`. Snake-case headers, outer whitespace trimming and known category case normalization are deterministic. Preserve text identifiers, internal punctuation and leading zeros. Do not fill missing amounts with zero. Remove only identical normalized rows; conflicting duplicate claim IDs stop the build. No rows were removed here.

Parse source dates as `%m/%d/%Y`, evidenced by unambiguous values such as 06/21/2024. Export ISO `YYYY-MM-DD`. Week = ISO week; weekday = ISO Monday 1 through Sunday 7. The date dimension contains observed service dates, not a claims-event calendar.

## Review flags

All flags use 1 for a condition requiring attention and 0 otherwise. A flag is not proof of source error, lost revenue, or incorrect clinical coding.

| Field | Rule for 1 | Treatment |
| --- | --- | --- |
| status_consistency_flag | Claim Status Denied with Outcome Paid/Partially Paid; or Claim Status Paid with Outcome Denied | Retain and review conflicting labels |
| status_ambiguity_flag | Under Review with Outcome Paid/Partially Paid | Retain as unresolved lifecycle ambiguity |
| ar_status_review_flag | Paid with AR Denied; Under Review with AR Closed; or Denied with AR Partially Paid | Review operational definitions and timing |
| monetary_anomaly_flag | Any negative amount, Allowed > Billed, Paid > Allowed, or Paid > Billed | Retain original values, including negative gaps |
| zero_amount_flag | Any of the three amounts equals zero | Retain; ratios with zero denominators are null |
| denied_with_payment_flag | Claim Status Denied and Paid Amount > 0 | Review status timing; do not zero payments |
| paid_with_allowed_gap_flag | Claim Status Paid and Allowed > Paid | Review interpretation of Paid and residuals |
| code_format_flag | Identifier or code fails an observed format below | Retain and review; no clinical-validity claim |

Claim Status Paid + Outcome Partially Paid is not included in the contradiction flag: the former may describe a workflow step. Under Review + Outcome Denied is also not labeled contradictory: a denied claim may be under review. Denied + AR Closed is not automatically an error: closure could follow a denial. Without lifecycle timestamps, the review rules intentionally avoid asserting a single correct lifecycle.

These rules give 315 status contradictions, 218 additional status ambiguities, and 168 AR review flags. There are 328 denied claims with positive payments and 329 Paid-status claims with a positive allowed amount gap. Flags can overlap and must not be summed to estimate distinct affected claims.

## Open AR rule

`open_ar_flag=1` only for Open, Pending, On Hold or Partially Paid (683 records). Closed is excluded. Denied is excluded from this operational open-status measure and reported separately, since recoverability is unknown. This is an explicit project grouping, not a financial AR classification. Gross unpaid on any grouping remains billed minus paid, not confirmed collectible AR.

## Observed format checks

- Claim ID: 10 uppercase alphanumeric characters.
- Provider ID and Patient ID: exactly 10 digits, stored as strings.
- Procedure Code: exactly 5 digits, stored as a string.
- Diagnosis Code: uppercase letter, 2 digits, decimal point and 1 digit.

These patterns match this synthetic input only. They must not be described as universal medical coding validation. No provider names, specialty, diagnoses, payer company names or patient demographics were inferred.

## Reporting limits

Currency is unspecified: use source currency units, not INR or USD. Reason Code contains descriptions, not standardized CARC/RARC codes. A reason appears on every claim, including Paid and Under Review; denial-reason analyses explicitly restrict to Claim Status Denied. The source contains no adjudication, submission, payment or snapshot timestamp. Service-date month is not cash-collection month. September contains services through the 20th, so MoM movements are not like-for-like performance changes.
