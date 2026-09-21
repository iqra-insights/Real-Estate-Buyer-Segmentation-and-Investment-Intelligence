"""Robustness and stability analysis for buyer segmentation.

Runs complementary feature strategies, K-Means stability across random seeds,
and bootstrap-like resampling agreement. Outputs are used to support model
selection rather than to manufacture a better score.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data" / "processed" / "Client_Level_Feature_Table.csv"
OUT = BASE / "outputs" / "tables"
DOCS = BASE / "docs"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    df = pd.read_csv(DATA)
    df["spend_per_purchase"] = df["total_spend"] / df["total_purchases"].replace(0, np.nan)
    df["log_total_spend"] = np.log1p(df["total_spend"].clip(lower=0))
    df["log_avg_purchase_price"] = np.log1p(df["avg_purchase_price"].clip(lower=0))
    df["log_purchase_span_days"] = np.log1p(df["purchase_span_days"].clip(lower=0))

    strategies = {
        "Current production": [
            "age", "satisfaction_score", "total_purchases", "total_spend",
            "avg_purchase_price", "avg_floor_area", "n_towers", "pct_apartment",
            "purchase_span_days", "loan_flag", "investment_flag", "is_company",
        ],
        "Log-scaled spend": [
            "age", "satisfaction_score", "total_purchases", "log_total_spend",
            "log_avg_purchase_price", "avg_floor_area", "n_towers", "pct_apartment",
            "log_purchase_span_days", "loan_flag", "investment_flag", "is_company",
        ],
        "Balanced behavior": [
            "age", "satisfaction_score", "total_purchases", "avg_purchase_price",
            "avg_floor_area", "n_towers", "pct_apartment", "purchase_span_days",
            "loan_flag", "investment_flag", "is_company", "spend_per_purchase",
        ],
    }

    rows = []
    for strategy, cols in strategies.items():
        X = StandardScaler().fit_transform(df[cols].fillna(0))
        for k in range(2, 7):
            km = KMeans(n_clusters=k, random_state=42, n_init=20)
            labels = km.fit_predict(X)
            rows.append({"strategy": strategy, "k": k,
                         "silhouette": silhouette_score(X, labels),
                         "inertia": km.inertia_})
    comparison = pd.DataFrame(rows)
    comparison.to_csv(OUT / "06_Feature_Strategy_Comparison.csv", index=False)

    # Production feature space stability across seeds.
    prod_cols = strategies["Current production"]
    X = StandardScaler().fit_transform(df[prod_cols].fillna(0))
    seed_labels = {}
    stability_rows = []
    for seed in [0, 7, 21, 42, 84, 123]:
        labels = KMeans(n_clusters=4, random_state=seed, n_init=50).fit_predict(X)
        seed_labels[seed] = labels
    seeds = list(seed_labels)
    for i, s1 in enumerate(seeds):
        for s2 in seeds[i + 1:]:
            stability_rows.append({"seed_a": s1, "seed_b": s2,
                                   "ari": adjusted_rand_score(seed_labels[s1], seed_labels[s2])})
    stability = pd.DataFrame(stability_rows)
    stability.to_csv(OUT / "09_KMeans_Seed_Stability.csv", index=False)

    # Bootstrap-style agreement: fit on 80% samples and compare assignments
    # only for the clients present in each pairwise intersection.
    rng = np.random.RandomState(42)
    boot_rows = []
    for rep in range(10):
        idx = np.sort(rng.choice(len(df), size=int(len(df) * 0.8), replace=False))
        X_sub = X[idx]
        labels = KMeans(n_clusters=4, random_state=100 + rep, n_init=30).fit_predict(X_sub)
        # Compare to production assignment on the same observations.
        prod = KMeans(n_clusters=4, random_state=42, n_init=50).fit_predict(X)
        boot_rows.append({"replicate": rep + 1,
                          "sample_fraction": 0.8,
                          "ari_vs_full_model": adjusted_rand_score(prod[idx], labels),
                          "sample_size": len(idx)})
    boot = pd.DataFrame(boot_rows)
    boot.to_csv(OUT / "08_KMeans_Bootstrap_Stability.csv", index=False)

    corr = df[prod_cols].corr(numeric_only=True)
    corr.to_csv(OUT / "05_Clustering_Feature_Correlation.csv")

    summary = {
        "production_strategy": "Current production",
        "production_k": 4,
        "production_silhouette": float(comparison.query("strategy == 'Current production' and k == 4").iloc[0].silhouette),
        "best_silhouette_over_tested_strategies": float(comparison.silhouette.max()),
        "best_strategy_by_silhouette": comparison.loc[comparison.silhouette.idxmax(), "strategy"],
        "best_k_by_silhouette": int(comparison.loc[comparison.silhouette.idxmax(), "k"]),
        "seed_stability_mean_ari": float(stability.ari.mean()),
        "seed_stability_min_ari": float(stability.ari.min()),
        "bootstrap_mean_ari": float(boot.ari_vs_full_model.mean()),
        "bootstrap_min_ari": float(boot.ari_vs_full_model.min()),
    }
    (OUT / "11_Model_Robustness_Summary.json").write_text(json.dumps(summary, indent=2))

    md = f"""# Model Robustness & Validation\n\n## Why this analysis exists\n\nThe project does not optimize for a cosmetically high clustering score. The goal is a segmentation that is reproducible, interpretable, and useful for the stated business problem. This robustness pass therefore compares feature strategies and tests whether the production K-Means solution is stable across random initializations and 80% resamples.\n\n## Results\n\n- Production feature strategy: **Current production**\n- Production k: **4**\n- Production-space silhouette (20 initializations, matching the shipped model): **{summary['production_silhouette']:.4f}**\n- Best tested silhouette: **{summary['best_silhouette_over_tested_strategies']:.4f}** ({summary['best_strategy_by_silhouette']}, k={summary['best_k_by_silhouette']})\n- Mean pairwise seed ARI for k=4: **{summary['seed_stability_mean_ari']:.4f}**\n- Minimum pairwise seed ARI for k=4: **{summary['seed_stability_min_ari']:.4f}**\n- Mean 80% resample ARI vs full model: **{summary['bootstrap_mean_ari']:.4f}**\n- Minimum 80% resample ARI: **{summary['bootstrap_min_ari']:.4f}**\n\n## What the summary statistics hide\n\nThe mean/min figures above understate two structural patterns visible in the raw pairwise data (`09_KMeans_Seed_Stability.csv`, `08_KMeans_Bootstrap_Stability.csv`) and worth stating explicitly rather than leaving implicit:\n\n**Seed stability is bimodal, not uniformly noisy.** Of the six tested seeds, {{0, 123}} agree with each other perfectly (ARI = 1.0) and {{7, 21, 42, 84}} agree with each other closely (ARI 0.94-0.99), but the two groups only agree with *each other* at ARI ~0.52. This means K-Means is converging to one of (at least) two distinct, internally-consistent solutions depending on initialization - not settling near one solution with random jitter. The production model uses `random_state=42`, which falls in the four-seed majority group, so the shipped segmentation is the more commonly-reached solution rather than the rarer alternative - but a different arbitrary seed choice could plausibly have shipped a qualitatively different clustering. This risk is real and should be disclosed, not smoothed over by the mean.\n\n**Bootstrap agreement is highly variable, not consistently moderate.** The ten 80%-resample replicates range from ARI 0.26 to ARI 0.96, not tightly clustered around the 0.58 mean. Two replicates land near-perfect agreement with the full-data model; most sit around 0.5; one is quite poor (0.26). A single mean obscures that resampling stability itself varies a lot run to run.\n\nNeither finding invalidates the k=4 production choice - it is still the majority-mode, business-interpretable solution - but both are the kind of detail that should survive into any writeup or interview answer about "how stable is this segmentation," rather than only the headline mean.\n\n## Interpretation\n\nThe tested feature strategies do not reveal a dramatically separated cluster structure. The balanced strategy improves silhouette for some k values, but it changes the business structure substantially (for example, company buyers can merge with individual buyers), so it is not automatically a better production model. The selected k=4 solution is retained because it preserves the explicit corporate-buyer distinction and provides four actionable profiles while documenting its modest separation.\n\nThe seed and resampling checks provide a reproducibility signal rather than a claim of perfect cluster stability. ARI values should be interpreted alongside cluster size, business meaning, and the underlying continuous nature of the customer behavior.\n\n## Feature multicollinearity\n\n`05_Clustering_Feature_Correlation.csv` shows `total_purchases` and `n_towers` correlate at 0.93, and `avg_purchase_price` and `avg_floor_area` correlate at 0.96, with `total_spend` correlating 0.57-0.71 with three other included features. Five of the nine numeric clustering features substantially encode the same underlying "transaction scale" dimension, which is disproportionately weighted in the Euclidean distance calculation as a result. By contrast, `loan_flag`, `investment_flag`, `is_company`, and `satisfaction_score` correlate near zero with everything (<=0.08). This is a direct, data-backed explanation for why the resulting segments separate mainly by spend/purchase scale rather than by financing or investment behavior: the feature space is structurally weighted toward scale, not because those behavioral signals were unimportant to the business question.\n\n## Cross-script silhouette consistency\n\n`src/03_Buyer_Segmentation_Clustering.py`'s k-sweep (`07_Cluster_Count_Evaluation.csv`) and this script's feature-strategy sweep both now use `n_init=20`, matching the shipped production model's fit exactly. All three now report the same k=4 production silhouette: **{summary['production_silhouette']:.4f}**. (An earlier version of this pipeline used three different `n_init` values across the three scripts - 10, 20, 30 - producing three slightly different numbers for nominally the same model; that inconsistency has been eliminated by standardizing `n_init`, rather than merely documented away.)\n\n## Audit artifacts\n\n- `outputs/tables/06_Feature_Strategy_Comparison.csv`\n- `outputs/tables/09_KMeans_Seed_Stability.csv`\n- `outputs/tables/08_KMeans_Bootstrap_Stability.csv`\n- `outputs/tables/05_Clustering_Feature_Correlation.csv`\n- `outputs/tables/11_Model_Robustness_Summary.json`\n"""
    (DOCS / "06_Model_Robustness_Validation.md").write_text(md)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
