"""
Data Audit, Cleaning & Feature Engineering
Machine Learning-Based Buyer Segmentation and Investment Profiling
-------------------------------------------------------------------
Loads the two raw files (Client_Master_Raw_Data.csv, Property_Transactions_Raw_Data.csv), cleans them,
aggregates properties up to client level (one client -> many purchases),
and produces a single client-level feature table ready for clustering.
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_raw():
    clients = pd.read_csv(RAW_DIR / "Client_Master_Raw_Data.csv")
    properties = pd.read_csv(RAW_DIR / "Property_Transactions_Raw_Data.csv")
    return clients, properties


def clean_clients(clients: pd.DataFrame) -> pd.DataFrame:
    df = clients.copy()

    # Normalize categorical text (defensive - source data is already clean,
    # but this makes the pipeline robust to future/messier extracts)
    text_cols = ["client_type", "gender", "country", "region",
                 "acquisition_purpose", "loan_applied", "referral_channel"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    # Robust date-of-birth parsing: the raw column mixes DD-MM-YYYY and
    # MM/DD/YYYY style strings, so we let pandas infer per-value format
    # rather than forcing one and silently corrupting the other.
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], format="mixed", errors="coerce")

    reference_date = pd.Timestamp("2025-12-31")  # latest transaction month in the data
    df["age"] = ((reference_date - df["date_of_birth"]).dt.days / 365.25).round(1)

    # Sanity-check age; flag rather than silently drop
    bad_age = df[(df["age"] < 18) | (df["age"] > 100)]
    if len(bad_age) > 0:
        print(f"WARNING: {len(bad_age)} clients have implausible ages after DOB parsing.")

    # Binary flags for clustering
    df["loan_flag"] = df["loan_applied"].map({"Yes": 1, "No": 0})
    df["investment_flag"] = df["acquisition_purpose"].map({"Investment": 1, "Home": 0})
    df["is_company"] = df["client_type"].map({"Company": 1, "Individual": 0})

    # Duplicate check
    dup_ids = df["client_id"].duplicated().sum()
    if dup_ids > 0:
        print(f"WARNING: {dup_ids} duplicate client_id rows found - keeping first occurrence.")
        df = df.drop_duplicates(subset="client_id", keep="first")

    return df


def clean_properties(properties: pd.DataFrame) -> pd.DataFrame:
    df = properties.copy()

    df["sale_price_num"] = (
        df["sale_price"].astype(str).str.replace(r"[\$,]", "", regex=True).astype(float)
    )
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="mixed", errors="coerce")
    df["unit_category"] = df["unit_category"].astype(str).str.strip()
    df["listing_status"] = df["listing_status"].astype(str).str.strip()

    dup_ids = df["listing_id"].duplicated().sum()
    if dup_ids > 0:
        print(f"WARNING: {dup_ids} duplicate listing_id rows found - keeping first occurrence.")
        df = df.drop_duplicates(subset="listing_id", keep="first")

    return df


def build_client_purchase_features(properties: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate the transaction-level properties table up to one row per
    client, since a client can (and typically does) buy multiple units.
    Only SOLD listings carry a client_ref, so unsold inventory is
    excluded from these behavioral features by construction.
    """
    sold = properties[properties["listing_status"] == "Sold"].copy()

    agg = sold.groupby("client_ref").agg(
        total_purchases=("listing_id", "count"),
        total_spend=("sale_price_num", "sum"),
        avg_purchase_price=("sale_price_num", "mean"),
        max_purchase_price=("sale_price_num", "max"),
        avg_floor_area=("floor_area_sqft", "mean"),
        total_floor_area=("floor_area_sqft", "sum"),
        n_towers=("tower_number", "nunique"),
        first_purchase_date=("transaction_date", "min"),
        last_purchase_date=("transaction_date", "max"),
    ).reset_index().rename(columns={"client_ref": "client_id"})

    # Unit-type mix (share of Apartment vs Office purchases per client)
    unit_mix = (
        sold.groupby(["client_ref", "unit_category"]).size()
        .unstack(fill_value=0)
    )
    unit_mix = unit_mix.div(unit_mix.sum(axis=1), axis=0)
    unit_mix.columns = [f"pct_{c.lower()}" for c in unit_mix.columns]
    unit_mix = unit_mix.reset_index().rename(columns={"client_ref": "client_id"})

    agg = agg.merge(unit_mix, on="client_id", how="left")

    # Repeat-buyer flag and purchase span in days
    agg["is_repeat_buyer"] = (agg["total_purchases"] > 1).astype(int)
    agg["purchase_span_days"] = (agg["last_purchase_date"] - agg["first_purchase_date"]).dt.days

    return agg


def build_master_table():
    clients_raw, properties_raw = load_raw()
    clients = clean_clients(clients_raw)
    properties = clean_properties(properties_raw)

    purchase_features = build_client_purchase_features(properties)

    master = clients.merge(purchase_features, on="client_id", how="left")

    # Every client has >=1 purchase in this dataset (verified in data audit),
    # so no NaNs are expected here - but guard anyway for robustness.
    numeric_fill_cols = [c for c in purchase_features.columns if c != "client_id"]
    n_missing = master[numeric_fill_cols].isnull().any(axis=1).sum()
    if n_missing > 0:
        print(f"NOTE: {n_missing} clients have no recorded purchase - filling purchase features with 0.")
        master[numeric_fill_cols] = master[numeric_fill_cols].fillna(0)

    return master, clients, properties


if __name__ == "__main__":
    master, clients, properties = build_master_table()
    print("Clients cleaned:", clients.shape)
    print("Properties cleaned:", properties.shape)
    print("Master client-level table:", master.shape)
    print(master.head())

    master.to_csv(PROCESSED_DIR / "Client_Level_Feature_Table.csv", index=False)
    clients.to_csv(PROCESSED_DIR / "Client_Clean_Data.csv", index=False)
    properties.to_csv(PROCESSED_DIR / "Property_Clean_Data.csv", index=False)
    print(f"\nSaved processed files to {PROCESSED_DIR}")
