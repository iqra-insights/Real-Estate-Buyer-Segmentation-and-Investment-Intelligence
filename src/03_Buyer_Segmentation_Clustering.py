"""
Clustering pipeline for buyer segmentation.
Encodes + scales client-level features, fits K-Means across a range of k,
validates with Elbow + Silhouette, cross-checks with Hierarchical
clustering, and profiles the final segments.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import dendrogram, linkage

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE / "data" / "processed"
MODELS_DIR = BASE / "models"
FIG_DIR = BASE / "outputs" / "figures"
TABLE_DIR = BASE / "outputs" / "tables"
for d in (MODELS_DIR, FIG_DIR, TABLE_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Features used for clustering. client_id is an identifier -> excluded.
# Names/dates are excluded; behavioral + demographic signals are kept.
NUMERIC_FEATURES = [
    "age", "satisfaction_score", "total_purchases", "total_spend",
    "avg_purchase_price", "avg_floor_area", "n_towers",
    "pct_apartment", "purchase_span_days",
]
BINARY_FEATURES = ["loan_flag", "investment_flag", "is_company"]
# NOTE: is_repeat_buyer was tested and removed from clustering inputs -
# every client in this dataset has >=3 purchases (min=3), making
# is_repeat_buyer constant (=1) across all 2,000 rows. A zero-variance
# feature carries no clustering signal (StandardScaler reduces it to a
# constant 0 for every row) and, worse, it had misled the naming logic
# into calling one segment "Repeat" Buyers as if repeat purchasing were
# what distinguished it - when in fact 100% of clients are repeat buyers.
# The real differentiator for that segment is purchase FREQUENCY/VOLUME,
# which total_purchases (already in NUMERIC_FEATURES) captures correctly.
CATEGORICAL_FEATURES: list = []
# Note: country (10 levels) and region (57 levels) are deliberately excluded
# from the clustering INPUT space. One-hot encoding them and mixing with
# StandardScaler'd continuous variables was tested (see docs/05_Model_Notes.md)
# and measurably diluted cluster separation (lower silhouette) without
# adding interpretable structure - geography is analyzed post-hoc instead,
# by cross-tabulating the resulting cluster labels against country/region.


def load_master():
    df = pd.read_csv(PROCESSED_DIR / "Client_Level_Feature_Table.csv")
    # pct_apartment may be missing if a client bought only offices (pct_office=1);
    # ensure both mix columns exist and are filled.
    if "pct_apartment" not in df.columns:
        df["pct_apartment"] = 0.0
    df["pct_apartment"] = df["pct_apartment"].fillna(0.0)
    return df


def build_feature_matrix(df: pd.DataFrame):
    transformers = [("num", StandardScaler(), NUMERIC_FEATURES + BINARY_FEATURES)]
    if CATEGORICAL_FEATURES:
        transformers.append(
            ("cat", OneHotEncoder(handle_unknown="ignore", drop=None), CATEGORICAL_FEATURES)
        )
    preprocessor = ColumnTransformer(transformers=transformers)
    X = preprocessor.fit_transform(df)
    feature_names = list(NUMERIC_FEATURES) + list(BINARY_FEATURES)
    if CATEGORICAL_FEATURES:
        feature_names += list(
            preprocessor.named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES)
        )
    return X, preprocessor, feature_names


def evaluate_k_range(X, k_min=2, k_max=10):
    inertias, sil_scores = [], []
    ks = list(range(k_min, k_max + 1))
    for k in ks:
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(X)
        inertias.append(model.inertia_)
        sil_scores.append(silhouette_score(X, labels))
    return ks, inertias, sil_scores


def plot_elbow_silhouette(ks, inertias, sil_scores):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(ks, inertias, marker="o", color="#2563eb")
    axes[0].set_title("Elbow Method")
    axes[0].set_xlabel("Number of clusters (k)")
    axes[0].set_ylabel("Inertia")
    axes[0].grid(alpha=0.3)

    axes[1].plot(ks, sil_scores, marker="o", color="#059669")
    axes[1].set_title("Silhouette Score")
    axes[1].set_xlabel("Number of clusters (k)")
    axes[1].set_ylabel("Silhouette score")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "10_Cluster_Selection_Diagnostics.png", dpi=150)
    plt.close()


def plot_dendrogram(X, sample_size=300):
    # Hierarchical clustering / dendrograms are O(n^2) - sample for readability
    rng = np.random.RandomState(42)
    idx = rng.choice(X.shape[0], size=min(sample_size, X.shape[0]), replace=False)
    X_sample = X[idx] if not hasattr(X, "toarray") else X[idx].toarray()

    Z = linkage(X_sample, method="ward")
    plt.figure(figsize=(12, 5))
    dendrogram(Z, truncate_mode="lastp", p=30, leaf_rotation=90)
    plt.title(f"Hierarchical Clustering Dendrogram (sample of {len(idx)} clients, Ward linkage)")
    plt.xlabel("Cluster size (truncated)")
    plt.ylabel("Distance")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "13_Hierarchical_Clustering_Cross_Check.png", dpi=150)
    plt.close()


def fit_final_kmeans(X, k):
    model = KMeans(n_clusters=k, random_state=42, n_init=20)
    labels = model.fit_predict(X)
    return model, labels


def compare_with_hierarchical(X, k, kmeans_labels, sample_size=1000):
    """Cross-validate K-Means against Hierarchical clustering via
    Adjusted Rand Index on a matching sample."""
    from sklearn.metrics import adjusted_rand_score
    rng = np.random.RandomState(42)
    idx = rng.choice(X.shape[0], size=min(sample_size, X.shape[0]), replace=False)
    X_sample = X[idx] if not hasattr(X, "toarray") else X[idx].toarray()

    hier = AgglomerativeClustering(n_clusters=k, linkage="ward")
    hier_labels = hier.fit_predict(X_sample)
    ari = adjusted_rand_score(np.array(kmeans_labels)[idx], hier_labels)
    return ari


def name_segments(profile: pd.DataFrame) -> dict:
    """
    Assign human-readable, collision-free business names to clusters,
    ranking clusters against EACH OTHER on the metrics that actually
    separate them (rather than fixed thresholds, which can - and did,
    on the first pass - assign the same label to two different clusters).
    """
    names = {}
    remaining = list(profile.index)

    # 1. Company-dominated cluster(s) are unambiguous and named first.
    company_clusters = [c for c in remaining if profile.loc[c, "is_company"] >= 0.5]
    for c in company_clusters:
        names[c] = "Corporate Buyers"
    individual_clusters = [c for c in remaining if c not in company_clusters]

    if individual_clusters:
        ind_profile = profile.loc[individual_clusters]

        # Highest average price-per-unit among individual buyers = premium segment
        premium_cluster = ind_profile["avg_purchase_price"].idxmax()
        names[premium_cluster] = "Premium / High-Value Buyers"

        remaining_ind = [c for c in individual_clusters if c != premium_cluster]
        if remaining_ind:
            rest_profile = ind_profile.loc[remaining_ind]

            # Highest purchase frequency among what's left = high-volume buyers
            # (NOT "repeat buyers" - every client in this dataset is a repeat
            # buyer, min 3 purchases each, so that wouldn't be a real distinction)
            repeat_cluster = rest_profile["total_purchases"].idxmax()
            names[repeat_cluster] = "High-Volume / Frequent Buyers"

            remaining_ind2 = [c for c in remaining_ind if c != repeat_cluster]
            if remaining_ind2:
                rest_profile2 = rest_profile.loc[remaining_ind2]
                # Lowest total spend among what's left = value-conscious segment
                value_cluster = rest_profile2["total_spend"].idxmin()
                names[value_cluster] = "Value-Conscious Home Buyers"

                # Any further leftover clusters (k > 4) get a generic
                # numbered label rather than a fabricated distinction.
                for c in remaining_ind2:
                    if c != value_cluster and c not in names:
                        names[c] = f"Individual Buyers (Segment {c})"

    return names


def run():
    df = load_master()
    X, preprocessor, feature_names = build_feature_matrix(df)

    print("Evaluating k = 2..10 ...")
    ks, inertias, sil_scores = evaluate_k_range(X, 2, 10)
    plot_elbow_silhouette(ks, inertias, sil_scores)
    for k, i, s in zip(ks, inertias, sil_scores):
        print(f"  k={k}: inertia={i:.1f}, silhouette={s:.4f}")

    best_k_by_silhouette = ks[int(np.argmax(sil_scores))]
    print(f"\nBest k by silhouette score alone: {best_k_by_silhouette}")

    plot_dendrogram(X)

    return df, X, preprocessor, feature_names, ks, inertias, sil_scores


if __name__ == "__main__":
    df, X, preprocessor, feature_names, ks, inertias, sil_scores = run()

    # Save interim eval table
    pd.DataFrame({"k": ks, "inertia": inertias, "silhouette_score": sil_scores}).to_csv(
        TABLE_DIR / "07_Cluster_Count_Evaluation.csv", index=False
    )
    print("Saved elbow/silhouette figure and k-evaluation table.")

    # ------------------------------------------------------------------
    # Final k selection: silhouette peaks at k=3 (0.145) but is nearly
    # flat across k=3..8 (0.12-0.15) - there is no sharp natural cluster
    # structure in this dataset (expected for a mostly-independent set of
    # demographic + behavioral fields). Rather than chase the marginal
    # silhouette gain of k=3, we select k=4: it matches the elbow's next
    # bend, produces well-populated, business-interpretable segments, and
    # aligns with the four buyer archetypes the business asked about.
    # This choice is documented, not hidden - see docs/05_Model_Notes.md.
    # ------------------------------------------------------------------
    BEST_K = 4
    final_model, labels = fit_final_kmeans(X, BEST_K)
    df["cluster"] = labels

    final_silhouette = silhouette_score(X, labels)
    ari = compare_with_hierarchical(X, BEST_K, labels)
    print(f"\nFinal model: k={BEST_K}, silhouette={final_silhouette:.4f}, "
          f"Adjusted Rand Index vs Hierarchical={ari:.4f}")

    # Cluster sizes
    sizes = df["cluster"].value_counts().sort_index()
    print("\nCluster sizes:\n", sizes)

    # Cluster profile (mean of key features per cluster)
    profile_cols = ["age", "satisfaction_score", "total_purchases", "total_spend",
                     "avg_purchase_price", "avg_floor_area", "pct_apartment",
                     "loan_flag", "investment_flag", "is_company"]
    profile = df.groupby("cluster")[profile_cols].mean().round(3)
    profile["size"] = sizes

    # Gender is a listed demographic field in the PRD's "cluster interpretation"
    # requirement but is categorical (not meaningfully averaged), so it is
    # reported as a separate composition table rather than mixed into the
    # numeric profile above.
    gender_mix = pd.crosstab(df["cluster"], df["gender"], normalize="index").round(3)
    gender_mix.columns = [f"pct_{g.lower()}" for g in gender_mix.columns]
    print("\nGender mix by cluster:\n", gender_mix)
    print("\nCluster profile:\n", profile)

    segment_names = name_segments(profile)
    df["segment_name"] = df["cluster"].map(segment_names)
    print("\nSegment names:", segment_names)

    # Geographic cross-tab (post-hoc, not part of clustering input)
    geo_crosstab = pd.crosstab(df["segment_name"], df["country"], normalize="index").round(3)

    # Save everything the Streamlit app and research paper will need
    profile_out = profile.copy()
    profile_out["segment_name"] = profile_out.index.map(segment_names)
    profile_out.to_csv(TABLE_DIR / "04_Buyer_Segment_Profile.csv")
    gender_mix.to_csv(TABLE_DIR / "03_Segment_Gender_Mix.csv")
    geo_crosstab.to_csv(TABLE_DIR / "02_Segment_by_Country_Crosstab.csv")
    df.to_csv(PROCESSED_DIR / "Buyer_Segmentation_Results.csv", index=False)

    joblib.dump(final_model, MODELS_DIR / "Buyer_Segmentation_KMeans_Model.pkl")
    joblib.dump(preprocessor, MODELS_DIR / "Buyer_Segmentation_Preprocessor.pkl")
    joblib.dump({"k": BEST_K, "silhouette": final_silhouette, "ari_vs_hierarchical": ari,
                 "segment_names": segment_names, "feature_names": feature_names},
                MODELS_DIR / "Buyer_Segmentation_Model_Metadata.pkl")

    # Cluster distribution chart
    plt.figure(figsize=(7, 4.5))
    sizes_named = df["segment_name"].value_counts()
    plt.bar(sizes_named.index, sizes_named.values, color="#2563eb")
    plt.title("Buyer Segment Distribution")
    plt.ylabel("Number of clients")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "11_Final_Buyer_Segment_Distribution.png", dpi=150)
    plt.close()

    # Cluster profile comparison chart (the numeric profile table as a visual)
    plot_cols = ["age", "total_purchases", "avg_purchase_price", "satisfaction_score"]
    fig, axes = plt.subplots(1, len(plot_cols), figsize=(4 * len(plot_cols), 4))
    for ax, col in zip(axes, plot_cols):
        vals = profile.set_index(profile["segment_name"])[col] if "segment_name" in profile.columns else profile[col]
        seg_vals = df.groupby("segment_name")[col].mean().reindex(sizes_named.index)
        ax.bar(seg_vals.index, seg_vals.values, color="#2563eb")
        ax.set_title(col.replace("_", " ").title())
        ax.tick_params(axis="x", rotation=30, labelsize=8)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "12_Final_Segment_Profile.png", dpi=150)
    plt.close()

    print(f"\nSaved: Buyer_Segmentation_Results.csv, 04_Buyer_Segment_Profile.csv, 02_Segment_by_Country_Crosstab.csv, "
          f"model artifacts (Buyer_Segmentation_KMeans_Model.pkl, Buyer_Segmentation_Preprocessor.pkl, Buyer_Segmentation_Model_Metadata.pkl).")
