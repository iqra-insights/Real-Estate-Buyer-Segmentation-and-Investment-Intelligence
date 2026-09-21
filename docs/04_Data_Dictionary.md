# Data Dictionary (based on actual files supplied, not assumed schema)

## `data/raw/Client_Master_Raw_Data.csv` (2,000 rows, 0 missing, 0 duplicates)

| Column | Type | Values / Notes |
|---|---|---|
| client_id | ID | Unique, e.g. `C0001` |
| client_type | Categorical | `Individual`, `Company` |
| first_name, last_name | Text | Not used in modeling (PII) |
| date_of_birth | Date | **Mixed formats** (`DD-MM-YYYY` and `MM/DD/YYYY` both present) — parsed with `format="mixed"` |
| gender | Categorical | `F`, `M` |
| country | Categorical | 10 countries: USA, Canada, Germany, Belgium, Mexico, Russia, UK, Denmark, France, Australia |
| region | Categorical | 57 sub-regions (states/provinces) — high cardinality, used for geographic reporting only, not clustering input |
| acquisition_purpose | Categorical | `Home`, `Investment` (PRD listed "Personal use"; actual value is `Home`) |
| satisfaction_score | Numeric | Integer 1–5 |
| loan_applied | Categorical | `Yes`, `No` |
| referral_channel | Categorical | `Website`, `Agency`, `Client` (only 3 values, not open-ended) |

## `data/raw/Property_Transactions_Raw_Data.csv` (10,000 rows)

| Column | Type | Values / Notes |
|---|---|---|
| listing_id | ID | Unique |
| tower_number | Numeric | 1–20 |
| transaction_date | Date | Jan 2024 – Dec 2025, mixed formats |
| unit_category | Categorical | `Apartment`, `Office` |
| unit_number | Numeric | Unit number within tower |
| floor_area_sqft | Numeric | 410–1,957 sqft |
| sale_price | Text→Numeric | Stored as `"$300,385.62"` — stripped of `$`/`,` before casting to float |
| listing_status | Categorical | `Sold` (7,305 rows), `Available` (2,695 rows) |
| client_ref | FK → client_id | **Null for all 2,695 `Available` listings** (no buyer yet); populated for all 7,305 `Sold` listings; every non-null value matches a real `client_id` |

## Key structural finding

This is a **one-client-to-many-properties** relationship (every one of the 2,000 clients has purchased at least one unit; one client purchased as many as 13). A naive `clients.merge(properties, on='client_id')` would duplicate each client's demographic row once per property purchased and corrupt any clustering built directly on the merged rows.

**Resolution used in `src/01_Data_Preprocessing.py`:** aggregate `Property_Transactions_Raw_Data.csv` (Sold rows only) up to one row per `client_id` first — `total_purchases`, `total_spend`, `avg_purchase_price`, `avg_floor_area`, unit-type mix, tower diversity, purchase span — then join that one-to-one onto `Client_Master_Raw_Data.csv`. This produces genuine investment-behavior features instead of the shallow single-purchase view implied by the original PRD schema.

## Engineered client-level features (`data/processed/Client_Level_Feature_Table.csv`)

| Feature | Description |
|---|---|
| age | Derived from date_of_birth, reference date 2025-12-31 |
| loan_flag, investment_flag, is_company | Binary encodings of loan_applied, acquisition_purpose, client_type |
| total_purchases | Count of Sold units per client |
| total_spend | Sum of sale_price across a client's purchases |
| avg_purchase_price, max_purchase_price | Price statistics per client |
| avg_floor_area, total_floor_area | Floor area statistics per client |
| n_towers | Number of distinct towers a client has bought in |
| pct_apartment, pct_office | Unit-type mix per client |
| is_repeat_buyer | 1 if total_purchases > 1. **Constant (=1) for all 2,000 clients** — every client made at least 3 purchases, so this carries no discriminative signal and is excluded from clustering inputs (kept in the table only as a factual field). |
| purchase_span_days | Days between first and last purchase |
