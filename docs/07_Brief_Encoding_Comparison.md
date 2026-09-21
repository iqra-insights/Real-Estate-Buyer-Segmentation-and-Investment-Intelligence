# Brief-Compliant Encoding — Literal Step 2 Implementation & Comparison

## What this tests

The original project brief's Step 2 specifies encoding `client_type`, `region`,
`acquisition_purpose`, `referral_channel`, and `country` via One-Hot or Label
Encoding, and Step 3 names `age` and `satisfaction_score` as the fields to
scale. This script (`src/05_Brief_Encoding_Validation.py`) builds that
EXACT feature space - not an approximation of it - and runs the same K-Means
evaluation used everywhere else in this project, so the brief's literal
methodology is actually executed and measured, not just described.

## Results (raw numbers)

| Approach | Best k | Best silhouette |
|---|---|---|
| Brief Step 2 - One-Hot Encoding | 2 | 0.1634 |
| Brief Step 2 - Label Encoding | 2 | **0.4126** (highest of all three) |
| Production model (this project's final choice) | 3 | 0.1451 |

Full k=2..10 sweep for all three in `outputs/tables/01_Brief_vs_Production_Model_Comparison.csv`.

## Why the higher scores above are misleading, not better

Raw silhouette says the brief's literal encoding "wins." Inspecting what each
top-scoring clustering actually splits on shows why that number cannot be
taken at face value:

**Label Encoding, k=2** produces clusters of 0 Company / 1897 Individual
and 103 Company / 0 Individual - a **perfect, trivial
reproduction of the already-known client_type column**, not a discovery.
Label-encoding a 2-category nominal field as 0/1 and standard-scaling it
hands K-Means a pre-made, perfectly-separable axis; the high silhouette
score reflects that artifact, not meaningful multi-dimensional segmentation.

**One-Hot Encoding, k=2** splits almost entirely on `satisfaction_score`
(cluster means 1.49 vs 4.00 on
a 1-5 scale, a gap of 2.51). With only 2 dense numeric
features (age, satisfaction_score) set against 74 sparse one-hot columns
(57 from `region` alone, each covering only a handful of clients), the
dense numeric features end up dominating the Euclidean distance calculation
almost by default. This is effectively a low-satisfaction-vs-high-satisfaction
split, not a segmentation reflecting the five categorical fields the brief
asked to encode.

## Why the production model is preferred despite its lower silhouette

The production model's silhouette (0.1405 at k=4) is lower in raw number
terms, but it reflects genuine multi-dimensional buyer behavior - spend,
purchase frequency, financing, and company status all contribute meaningfully
to the resulting clusters (see `outputs/tables/04_Buyer_Segment_Profile.csv`). Neither
brief-compliant alternative achieves that: one collapses to an existing
label, the other collapses to a single numeric field. **Silhouette score
alone cannot distinguish a genuine multi-dimensional segmentation from a
degenerate single-variable split** - cluster composition has to be inspected
directly, which is what this script does rather than reporting the number
in isolation.

## Conclusion

The brief's methodology was followed to the letter, not skipped, and its
result is reported exactly as measured - including the inconvenient fact
that its raw silhouette is numerically higher. The production model is still
the right choice, for a reason more substantive than "the metric is better":
it is the one alternative, out of three tested, whose clusters do not
degenerate into either a copy of an input column or a single feature's
median split.
