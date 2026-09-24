-- Portable PostgreSQL / DuckDB DDL. Run in a new, empty project database.
CREATE TABLE stg_claims (
  claim_id TEXT NOT NULL,
  provider_id TEXT NOT NULL,
  patient_id TEXT NOT NULL,
  date_of_service TEXT NOT NULL,
  billed_amount TEXT NOT NULL,
  procedure_code TEXT NOT NULL,
  diagnosis_code TEXT NOT NULL,
  allowed_amount TEXT NOT NULL,
  paid_amount TEXT NOT NULL,
  insurance_type TEXT NOT NULL,
  claim_status TEXT NOT NULL,
  reason_code TEXT NOT NULL,
  follow_up_required TEXT NOT NULL,
  ar_status TEXT NOT NULL,
  outcome TEXT NOT NULL
);
CREATE TABLE dim_provider (provider_key INTEGER PRIMARY KEY, provider_id TEXT NOT NULL UNIQUE);
CREATE TABLE dim_patient (patient_key INTEGER PRIMARY KEY, patient_id TEXT NOT NULL UNIQUE);
CREATE TABLE dim_insurance (insurance_key INTEGER PRIMARY KEY, insurance_type TEXT NOT NULL UNIQUE);
CREATE TABLE dim_procedure (procedure_key INTEGER PRIMARY KEY, procedure_code TEXT NOT NULL UNIQUE);
CREATE TABLE dim_diagnosis (diagnosis_key INTEGER PRIMARY KEY, diagnosis_code TEXT NOT NULL UNIQUE);
CREATE TABLE dim_reason (reason_key INTEGER PRIMARY KEY, reason_code TEXT NOT NULL UNIQUE);
CREATE TABLE dim_date (date_key INTEGER PRIMARY KEY, full_date DATE NOT NULL UNIQUE, year INTEGER, month INTEGER, month_name TEXT, quarter INTEGER, week INTEGER, day_of_week INTEGER, service_month_start DATE);
CREATE TABLE fact_claims (
  claim_key INTEGER PRIMARY KEY,
  claim_id TEXT NOT NULL UNIQUE,
  provider_key INTEGER NOT NULL REFERENCES dim_provider(provider_key),
  patient_key INTEGER NOT NULL REFERENCES dim_patient(patient_key),
  insurance_key INTEGER NOT NULL REFERENCES dim_insurance(insurance_key),
  procedure_key INTEGER NOT NULL REFERENCES dim_procedure(procedure_key),
  diagnosis_key INTEGER NOT NULL REFERENCES dim_diagnosis(diagnosis_key),
  reason_key INTEGER NOT NULL REFERENCES dim_reason(reason_key),
  date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
  billed_amount NUMERIC(18,2) NOT NULL,
  allowed_amount NUMERIC(18,2) NOT NULL,
  paid_amount NUMERIC(18,2) NOT NULL,
  claim_status TEXT NOT NULL,
  follow_up_required TEXT NOT NULL,
  ar_status TEXT NOT NULL,
  outcome TEXT NOT NULL,
  gross_unpaid_amount NUMERIC(18,2),
  allowed_amount_gap NUMERIC(18,2),
  billed_to_allowed_ratio DOUBLE PRECISION,
  paid_to_billed_ratio DOUBLE PRECISION,
  paid_to_allowed_ratio DOUBLE PRECISION,
  claim_status_denied_flag INTEGER CHECK (claim_status_denied_flag IN (0,1)),
  outcome_denied_flag INTEGER CHECK (outcome_denied_flag IN (0,1)),
  any_denial_flag INTEGER CHECK (any_denial_flag IN (0,1)),
  follow_up_flag INTEGER CHECK (follow_up_flag IN (0,1)),
  open_ar_flag INTEGER CHECK (open_ar_flag IN (0,1)),
  status_consistency_flag INTEGER CHECK (status_consistency_flag IN (0,1)),
  status_ambiguity_flag INTEGER CHECK (status_ambiguity_flag IN (0,1)),
  ar_status_review_flag INTEGER CHECK (ar_status_review_flag IN (0,1)),
  monetary_anomaly_flag INTEGER CHECK (monetary_anomaly_flag IN (0,1)),
  zero_amount_flag INTEGER CHECK (zero_amount_flag IN (0,1)),
  denied_with_payment_flag INTEGER CHECK (denied_with_payment_flag IN (0,1)),
  paid_with_allowed_gap_flag INTEGER CHECK (paid_with_allowed_gap_flag IN (0,1)),
  code_format_flag INTEGER CHECK (code_format_flag IN (0,1))
);
