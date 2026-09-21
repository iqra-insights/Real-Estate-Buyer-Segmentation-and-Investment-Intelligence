# Model Robustness & Validation

## Why this analysis exists

The project does not optimize for a cosmetically high clustering score. The goal is a segmentation that is reproducible, interpretable, and useful for the stated business problem. This robustness pass therefore compares feature strategies and tests whether the production K-Means solution is stable across random initializations and 80% resamples.

## Results

- Production feature strategy: **Current production**
- Production k: **4**
- Production-space silhouette (20 initializations, matching the shipped model): **0.1405**
- Best tested silhouette: **0.1718** (Balanced behavior, k=3)
- Mean pairwise seed ARI for k=4: **0.7310**
- Minimum pairwise seed ARI for k=4: **0.5156**
- Mean 80% resample ARI vs full model: **0.5826**
- Minimum 80% resample ARI: **0.2633**

## What the summary statistics hide

The mean/min figures above understate two structural patterns visible in the raw pairwise data (`09_KMeans_Seed_Stability.csv`, `08_KMeans_Bootstrap_Stability.csv`) and worth stating explicitly rather than leaving implicit:

**Seed stability is bimodal, not uniformly noisy.** Of the six tested seeds, {0, 123} agree with each other perfectly (ARI = 1.0) and {7, 21, 42, 84} agree with each other closely (ARI 0.94-0.99), but the two groups only agree with *each other* at ARI ~0.52. This means K-Means is converging to one of (at least) two distinct, internally-consistent solutions depending on initialization - not settling near one solution with random jitter. The production model uses `random_state=42`, which falls in the four-seed majority group, so the shipped segmentation is the more commonly-reached solution rather than the rarer alternative - but a different arbitrary seed choice could plausibly have shipped a qualitatively different clustering. This risk is real and should be disclosed, not smoothed over by the mean.

**Bootstrap agreement is highly variable, not consistently moderate.** The ten 80%-resample replicates range from ARI 0.26 to ARI 0.96, not tightly clustered around the 0.58 mean. Two replicates land near-perfect agreement with the full-data model; most sit around 0.5; one is quite poor (0.26). A single mean obscures that resampling stability itself varies a lot run to run.

Neither finding invalidates the k=4 production choice - it is still the majority-mode, business-interpretable solution - but both are the kind of detail that should survive into any writeup or interview answer about "how stable is this segmentation," rather than only the headline mean.

## Interpretation

The tested feature strategies do not reveal a dramatically separated cluster structure. The balanced strategy improves silhouette for some k values, but it changes the business structure substantially (for example, company buyers can merge with individual buyers), so it is not automatically a better production model. The selected k=4 solution is retained because it preserves the explicit corporate-buyer distinction and provides four actionable profiles while documenting its modest separation.

The seed and resampling checks provide a reproducibility signal rather than a claim of perfect cluster stability. ARI values should be interpreted alongside cluster size, business meaning, and the underlying continuous nature of the customer behavior.

## Feature multicollinearity

`05_Clustering_Feature_Correlation.csv` shows `total_purchases` and `n_towers` correlate at 0.93, and `avg_purchase_price` and `avg_floor_area` correlate at 0.96, with `total_spend` correlating 0.57-0.71 with three other included features. Five of the nine numeric clustering features substantially encode the same underlying "transaction scale" dimension, which is disproportionately weighted in the Euclidean distance calculation as a result. By contrast, `loan_flag`, `investment_flag`, `is_company`, and `satisfaction_score` correlate near zero with everything (<=0.08). This is a direct, data-backed explanation for why the resulting segments separate mainly by spend/purchase scale rather than by financing or investment behavior: the feature space is structurally weighted toward scale, not because those behavioral signals were unimportant to the business question.

## Cross-script silhouette consistency

`src/03_Buyer_Segmentation_Clustering.py`'s k-sweep (`07_Cluster_Count_Evaluation.csv`) and this script's feature-strategy sweep both now use `n_init=20`, matching the shipped production model's fit exactly. All three now report the same k=4 production silhouette: **0.1405**. (An earlier version of this pipeline used three different `n_init` values across the three scripts - 10, 20, 30 - producing three slightly different numbers for nominally the same model; that inconsistency has been eliminated by standardizing `n_init`, rather than merely documented away.)

## Audit artifacts

- `outputs/tables/06_Feature_Strategy_Comparison.csv`
- `outputs/tables/09_KMeans_Seed_Stability.csv`
- `outputs/tables/08_KMeans_Bootstrap_Stability.csv`
- `outputs/tables/05_Clustering_Feature_Correlation.csv`
- `outputs/tables/11_Model_Robustness_Summary.json`
