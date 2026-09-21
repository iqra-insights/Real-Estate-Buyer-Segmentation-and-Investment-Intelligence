# Modeling Notes

## Correction log

**Fixed:** an earlier version of this pipeline included `is_repeat_buyer` (total_purchases > 1) as a clustering feature and named one cluster "Repeat Portfolio Buyers" on that basis. Audit of the final feature table showed `is_repeat_buyer` is **constant (=1) for all 2,000 clients** — the minimum purchase count in this dataset is 3, so every client is technically a repeat buyer. A constant feature carries no clustering signal (StandardScaler reduces it to 0 for every row, so it had zero effect on the actual cluster assignments), but the resulting name was misleading — it implied repeat purchasing was what distinguished that segment, when in fact 100% of clients qualify. The feature was removed from the clustering input list and the segment was renamed **"High-Volume / Frequent Buyers"**, reflecting its real distinguishing trait: purchase frequency well above the other segments (4.4 vs. 3.1-3.6 purchases/client), not repeat-buyer status per se. Re-running the pipeline confirmed cluster assignments and silhouette score (0.1405) are unchanged, as expected.

## Feature set decisions

## Why the brief's suggested segment labels were not used

The brief proposed four labels — Global Investors, First-Time Buyers, Corporate Buyers, Luxury Investors — each with an implied defining trait. Checking those traits directly against the actual cluster profile (`outputs/tables/04_Buyer_Segment_Profile.csv`) shows why forcing them on would have meant asserting things the data doesn't support:

| Brief label | Implied defining trait | What the data actually shows |
|---|---|---|
| First-Time Buyers | Younger, loan-dependent | Age ranges 54.6–57.7 across the three individual clusters — the *youngest* cluster overall is Corporate Buyers (47.6), already a separate, correctly-named group. Loan rate ranges only 34.3%–38.4% across individuals — no cluster is meaningfully "loan-dependent" relative to the others |
| Global Investors | High income, investment-purchase focused | Investment rate ranges only 27.8%–33.3% across all four clusters — no cluster is distinctly investment-oriented |
| Luxury Investors | High satisfaction, large investments | Satisfaction score ranges only 2.94–3.16 (on a 1–5 scale) across all four clusters — no cluster shows meaningfully higher satisfaction |
| Corporate Buyers | Companies purchasing multiple units | **This one matches**: `is_company` is 1.0 in one cluster and ≤0.002 in the other three — a real, sharp distinction. Used as-is. |

Only "Corporate Buyers" survives contact with the actual numbers. Labeling a segment "First-Time Buyers" when it is not the youngest group, or "Luxury Investors" when its satisfaction score is statistically indistinguishable from every other segment, would be a factually incorrect claim in the final deliverables — not a stylistic choice. The four segments actually used (Value-Conscious Home Buyers, High-Volume/Frequent Buyers, Premium/High-Value Buyers, Corporate Buyers) were named from the dimensions that *do* separate the data — purchase price, purchase frequency, and total spend — which is what the clustering algorithm was actually given to work with (see "Feature set decisions" below).

## Feature set decisions

**The brief's literal Step 2 encoding was actually implemented and tested, not skipped.** `src/05_Brief_Encoding_Validation.py` builds the exact feature space the brief specifies — One-Hot (and separately, Label) Encoding of `client_type`, `region`, `acquisition_purpose`, `referral_channel`, `country`, combined with the brief's Step 3 fields (`age`, `satisfaction_score`) only — and runs the identical K-Means evaluation used everywhere else in this project. Full results and a detailed writeup: `docs/07_Brief_Encoding_Comparison.md`.

The headline finding is counterintuitive and worth stating plainly: **both brief-compliant encodings score a numerically *higher* raw silhouette than the production model** (Label Encoding: 0.4126 at k=2; One-Hot: 0.1634 at k=2; production: 0.1451 at k=3). Inspecting what those top-scoring clusters actually contain shows why the number is misleading rather than better:
- Label Encoding's k=2 clusters are a **perfect, trivial reproduction of `client_type`** (0 Company/1897 Individual vs 103 Company/0 Individual) — label-encoding a 2-category field as 0/1 hands K-Means a pre-made, perfectly-separable axis. This isn't discovered structure, it's the input restated.
- One-Hot's k=2 clusters split almost entirely on `satisfaction_score` (means 1.49 vs 4.00) — with only 2 dense numeric features against 74 sparse one-hot columns (57 from `region` alone), the dense features dominate the distance calculation by default.

Neither is a genuine multi-dimensional segmentation. This is exactly why silhouette score cannot be read in isolation — cluster composition has to be inspected — and it's the concrete, measured justification (not merely an assumption) for why the production model uses behavioral/transactional features as clustering input and reserves geography for post-hoc profiling instead.

Two feature-set configurations were tested before finalizing the clustering inputs:

| Configuration | Silhouette (k=4) | Notes |
|---|---|---|
| Numeric + binary + one-hot(country, referral_channel, gender) | 0.1089 | High-cardinality one-hot columns diluted Euclidean distance |
| Numeric + binary only (final) | **0.1405** | Cleaner separation; categorical geography analyzed post-hoc instead |

`region` (57 levels) was excluded from clustering inputs entirely for the same reason, and is used only for post-hoc geographic breakdowns of the resulting segments.

## Cluster count (k) selection

| k | Inertia | Silhouette |
|---|---|---|
| 2 | 20,631.0 | 0.1381 |
| 3 | 18,556.7 | **0.1451 (max)** |
| 4 | 16,895.6 | 0.1405 |
| 5 | 15,812.6 | 0.1286 |
| 6 | 14,353.5 | 0.1308 |
| 7 | 13,616.9 | 0.1314 |
| 8 | 13,102.9 | 0.1322 |
| 9 | 12,655.0 | 0.1331 |
| 10 | 12,288.1 | 0.1352 |

(All computed with `n_init=20`, matching the final production fit exactly - see the Robustness & validation section below for why this matters.)

Silhouette scores are modest overall (0.12–0.15) and nearly flat from k=3 through k=8 — this dataset does not contain sharply separated natural clusters; buyer behavior varies more continuously than in hard groups. This is disclosed rather than hidden (see the Streamlit app's Model Information page).

**Final choice: k=4.** Rationale:
- The silhouette-optimal k=3 was tested, but merges the corporate-buyer signal into a broader individual-buyer cluster, losing an operationally important distinction (companies need a different sales motion than individuals).
- k=4 isolates `is_company` almost perfectly into its own cluster (the most genuinely distinct group in the data) and produces well-populated, interpretable segments.
- This mirrors the original PRD's request for a 4-segment view, but the segments themselves were named from the actual profiled data, not forced to match the PRD's assumed C1–C4 labels.

## Cross-validation against Hierarchical Clustering

Agglomerative (Ward-linkage) clustering was run on a 1,000-client sample and compared to the K-Means labels via Adjusted Rand Index: **ARI = 0.267**. This is a moderate, not strong, agreement — expected given the weak natural cluster structure noted above, and consistent with K-Means and Hierarchical clustering using different linkage/objective criteria on data without hard boundaries.

## Geographic concentration caveat

`09_Buyer_Distribution_by_Country.png` and `02_Segment_by_Country_Crosstab.csv` show the client base is **76.9% USA** (1,538 of 2,000 clients), with the remaining 9 countries ranging from 95 (UK) down to 15 (Denmark) clients. Any country-level breakdown for the smaller countries — e.g. an "investment rate by country" comparison — is statistically noisy for those small samples (a rate computed on 15 people swings enormously with just one or two different individuals) and should be read as indicative, not reliable, for anything outside the USA/UK/Canada range. The cluster-by-country crosstab shows all four segments sit within a narrow 73.8%-80.9% USA band, essentially mirroring the overall population - confirming that geography does not meaningfully differentiate the segments, which is consistent with (and validates) the decision to exclude country/region from the clustering inputs above.

## Brief terminology cross-reference

The original brief suggested four labels (Global Investors, First-Time Buyers, Corporate Buyers, Luxury Investors) before any clustering was run. Only "Corporate Buyers" matches exactly. This table maps each brief label to whichever actual segment is closest, and states plainly where the match breaks down — so both terminologies can be used without either overclaiming or silently dropping the brief's framing.

| Brief's suggested label | Closest actual segment | Match quality | Why |
|---|---|---|---|
| Corporate Buyers | **Corporate Buyers** | Exact | Company clients cluster cleanly on their own, exactly as the brief predicted. |
| Global Investors | Premium / High-Value Buyers (contested — see below) | Partial | Highest avg. purchase price ($432K) fits "high income," but investment_flag (30%) is not meaningfully higher than the other segments (28–34% across all four) — there is no segment that is distinctly investment-oriented. |
| Luxury Investors | Premium / High-Value Buyers (contested — see below) | Weak | Highest price again suggests "large investments," but satisfaction_score (3.01) is not the highest of the four (High-Volume Buyers scores higher at 3.16) — "high satisfaction" as described in the brief does not hold. |
| First-Time Buyers | Value-Conscious Home Buyers | Weak | Lowest avg. price fits a starter-buyer story, but this segment is not younger (age 55.5, versus 47.6–57.7 across all four — a 10-year spread with no segment under 47) and not more loan-dependent (38.4%, versus 34.3–42.2% across all four) than the others. "Younger, loan dependent" as the brief describes is not a pattern that exists in this data for any segment. |

**Why two brief labels (Global Investors, Luxury Investors) both point to the same actual segment, and why neither is a strong match:** age, loan rate, and satisfaction score simply do not vary much across the four real segments (age spans only 47.6–57.7; loan rate only 34.3–42.2%; satisfaction only 2.94–3.16). The real differentiator is purchase *scale* (price, frequency, volume), not the demographic/behavioral splits the brief anticipated. Forcing the brief's four names onto the actual clusters would mean asserting age or loan-dependency differences that the data does not show — which is why the production segments keep their data-derived names, with this table as the honest bridge between the two vocabularies.

## Robustness & validation

See `docs/06_Model_Robustness_Validation.md` (generated by `src/04_Model_Robustness_Validation.py`) for: a comparison against two alternative feature strategies, K-Means stability across 6 random seeds, stability under 80%-resample bootstrapping, and the feature-correlation matrix. Headline findings not to gloss over:
- Seed stability is **bimodal, not uniformly noisy**: two distinct stable solutions exist across random restarts (ARI≈1.0 within each, ARI≈0.52 between them). The production seed (42) lands in the 4-of-6 majority solution.
- `total_purchases`↔`n_towers` correlate at 0.93 and `avg_purchase_price`↔`avg_floor_area` at 0.96 - the clustering input space is structurally weighted toward transaction *scale*, which is the direct, data-backed reason segments separate by spend/volume rather than by financing/investment behavior.
- The current clustering and feature-validation pipelines standardize K-Means with `n_init=20`. The shipped production model therefore reports a reproducible k=4 silhouette of **0.1405**. Older exploratory runs used different `n_init` settings and produced lower values; those historical values are not part of the current production result.

## Final segments (k=4)

| Segment | Size | Naming logic |
|---|---|---|
| Value-Conscious Home Buyers | 812 | Individual buyers with the lowest total spend / avg purchase price among individual clusters |
| High-Volume / Frequent Buyers | 640 | Individual buyers with the highest purchase frequency (avg 4.4 purchases/client) |
| Premium / High-Value Buyers | 446 | Individual buyers with the highest average purchase price ($432K avg) |
| Corporate Buyers | 102 | `is_company = 1` in ~100% of the cluster |

Names were assigned by ranking clusters against each other on the metrics that actually separate them (spend, price, purchase frequency, company share) — not from fixed thresholds or the PRD's assumed labels.
