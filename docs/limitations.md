# Limitations

- Synthetic educational data only. No real patient information, provider performance, payer performance, hospital data, employment or production experience is claimed.
- No provenance or generation method was supplied beyond the user's synthetic-data contract. No Enigma Healthcare Solutions affiliation is asserted.
- Currency is absent. Amounts cannot be labeled INR/USD or compared with external financial benchmarks.
- Service date is the only source date. Aging, days in AR, collection timing, first-pass acceptance, appeals and time-to-resolution cannot be computed.
- September is partial through the 20th. No full-month September trend or forecast is asserted.
- Claim Status, Outcome and AR Status are not supplied with lifecycle definitions. Review flags are explicit project assumptions, not authoritative corrections.
- Every denied claim has a positive payment; 329 of 334 Paid-status claims retain an allowed amount gap. Denied billed value is not lost revenue; gross unpaid is not proven recoverable AR.
- Reasons are free-text categories across all statuses, not standardized denial codes or confirmed root causes.
- Each provider/patient has one claim, precluding meaningful repeat or longitudinal performance comparisons.
- No external clinical-code lookup, payer enrichment, demographics or causal inference was added.
- The notebook was executed locally and in Google Colab. The cloud runtime report and executed notebook are included; all 62 cloud checks passed.
- PostgreSQL semantics were tested in embedded PGlite. A separate PostgreSQL service, authentication, deployment and client-side psql load were not exercised.
- Four dashboards were rendered and tested in Tableau Public 2026.2 on Windows. The workbook is delivered locally; public hosting, mobile layout and screen-reader certification were not performed.
