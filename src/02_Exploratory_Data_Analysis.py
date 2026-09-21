"""
Exploratory Data Analysis - each chart answers a specific business
question rather than being a generic profiling dump.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE / "data" / "processed"
FIG_DIR = BASE / "outputs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["figure.facecolor"] = "white"
COLOR = "#2563eb"


def q_who_are_the_buyers(df):
    fig, ax = plt.subplots(figsize=(5, 4))
    df["client_type"].value_counts().plot(kind="bar", color=[COLOR, "#f59e0b"], ax=ax)
    ax.set_title("Who are the buyers? Individual vs Company")
    ax.set_ylabel("Number of clients")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "01_Buyer_Mix_by_Client_Type.png", dpi=150)
    plt.close()


def q_investment_by_client_type(df):
    ct = pd.crosstab(df["client_type"], df["acquisition_purpose"], normalize="index")
    fig, ax = plt.subplots(figsize=(5.5, 4))
    ct.plot(kind="bar", stacked=True, ax=ax, color=[COLOR, "#f59e0b"])
    ax.set_title("Are investment purchases more common among certain client types?")
    ax.set_ylabel("Share of clients")
    plt.xticks(rotation=0)
    plt.legend(title="Purpose")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "02_Acquisition_Purpose_by_Client_Type.png", dpi=150)
    plt.close()


def q_investment_by_region(df):
    top_countries = df["country"].value_counts().head(10).index
    ct = (df[df["country"].isin(top_countries)]
          .groupby("country")["investment_flag"].mean()
          .sort_values(ascending=False))
    fig, ax = plt.subplots(figsize=(7, 4))
    ct.plot(kind="bar", color=COLOR, ax=ax)
    ax.set_title("Which countries have the highest concentration of investment buyers?")
    ax.set_ylabel("Investment-purchase rate")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "03_Investment_Rate_by_Top_Country.png", dpi=150)
    plt.close()


def q_loan_by_clienttype(df):
    ct = pd.crosstab(df["client_type"], df["loan_applied"], normalize="index")
    fig, ax = plt.subplots(figsize=(5, 4))
    ct.plot(kind="bar", stacked=True, ax=ax, color=[COLOR, "#f59e0b"])
    ax.set_title("Does financing behavior differ across buyer groups?")
    ax.set_ylabel("Share of clients")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "04_Financing_Behavior_by_Client_Type.png", dpi=150)
    plt.close()


def q_referral_by_purpose(df):
    ct = pd.crosstab(df["referral_channel"], df["acquisition_purpose"], normalize="index")
    fig, ax = plt.subplots(figsize=(6, 4))
    ct.plot(kind="bar", stacked=True, ax=ax, color=[COLOR, "#f59e0b"])
    ax.set_title("Which referral channels bring the most investment-oriented buyers?")
    ax.set_ylabel("Share of clients")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "05_Acquisition_Purpose_by_Referral_Channel.png", dpi=150)
    plt.close()


def q_age_distribution(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(df["age"], bins=25, color=COLOR, edgecolor="white")
    ax.set_title("Buyer Age Distribution")
    ax.set_xlabel("Age")
    ax.set_ylabel("Number of clients")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "06_Buyer_Age_Distribution.png", dpi=150)
    plt.close()


def q_satisfaction_distribution(df):
    fig, ax = plt.subplots(figsize=(5, 4))
    df["satisfaction_score"].value_counts().sort_index().plot(kind="bar", color=COLOR, ax=ax)
    ax.set_title("Customer Satisfaction Score Distribution")
    ax.set_xlabel("Satisfaction score (1-5)")
    ax.set_ylabel("Number of clients")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "07_Customer_Satisfaction_Distribution.png", dpi=150)
    plt.close()


def missing_values_report(df):
    missing = df.isnull().sum()
    missing_pct = (df.isnull().mean() * 100).round(2)
    report = pd.DataFrame({"missing_count": missing, "missing_percentage": missing_pct})
    report = report[report["missing_count"] > 0].sort_values("missing_percentage", ascending=False)
    report.to_csv(BASE / "outputs" / "tables" / "10_Missing_Values_Report.csv")
    return report


def q_missing_values_chart(df):
    missing_pct = (df.isnull().mean() * 100).round(2)
    missing_pct = missing_pct[missing_pct >= 0]  # keep all columns, even 0%, for a complete picture
    fig, ax = plt.subplots(figsize=(8, 5))
    missing_pct.sort_values(ascending=True).plot(kind="barh", color=COLOR, ax=ax)
    ax.set_title("Missing Values by Column (client-level table, post-merge)")
    ax.set_xlabel("% missing")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "08_Data_Completeness_Audit.png", dpi=150)
    plt.close()


def q_country_distribution(df):
    fig, ax = plt.subplots(figsize=(7, 4))
    df["country"].value_counts().plot(kind="bar", color=COLOR, ax=ax)
    ax.set_title("Buyer Distribution by Country")
    ax.set_ylabel("Number of clients")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "09_Buyer_Distribution_by_Country.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    df = pd.read_csv(PROCESSED_DIR / "Client_Level_Feature_Table.csv")

    report = missing_values_report(df)
    print("Missing values in final client-level table (post-merge):")
    print(report if len(report) else "None - all client purchase features populated (every client has >=1 sale).")

    q_who_are_the_buyers(df)
    q_investment_by_client_type(df)
    q_investment_by_region(df)
    q_loan_by_clienttype(df)
    q_referral_by_purpose(df)
    q_age_distribution(df)
    q_satisfaction_distribution(df)
    q_missing_values_chart(df)
    q_country_distribution(df)

    print(f"\nSaved 9 EDA figures to {FIG_DIR}")
