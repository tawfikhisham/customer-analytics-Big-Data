import os
import sys
import subprocess
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


EXPECTED_COLUMNS = {
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
}


def safe_qcut(series: pd.Series, q: int, labels: list[str]) -> pd.Series:
    ranked = series.rank(method="first")
    return pd.qcut(ranked, q=q, labels=labels)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preprocess.py <csv-path>")
        sys.exit(1)

    input_path = sys.argv[1]
    df = pd.read_csv(input_path)

    missing_cols = EXPECTED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(
            "This solution expects the Online Retail dataset columns. "
            f"Missing columns: {sorted(missing_cols)}"
        )

    # ------------------------------
    # 1) Data cleaning
    # ------------------------------
    # Task 1: remove exact duplicate rows
    df = df.drop_duplicates().copy()

    # Task 2: fill missing textual product descriptions
    df["Description"] = df["Description"].fillna("Unknown Product")

    # Task 3: remove rows with missing customer ids
    df = df.dropna(subset=["CustomerID"]).copy()

    # Task 4: parse invoice date and drop invalid timestamps
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df = df.dropna(subset=["InvoiceDate"]).copy()

    # Task 5: remove cancellations and invalid transactional rows
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df = df[~df["InvoiceNo"].str.startswith("C")].copy()
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)].copy()

    # ------------------------------
    # 2) Feature transformation
    # ------------------------------
    # Task 1: convert customer id to integer for clean grouping
    df["CustomerID"] = df["CustomerID"].astype(int)

    # Task 2: create revenue per transaction line
    df["LineTotal"] = df["Quantity"] * df["UnitPrice"]

    # Task 3: derive behavioral time features
    df["InvoiceMonth"] = df["InvoiceDate"].dt.month
    df["InvoiceHour"] = df["InvoiceDate"].dt.hour
    df["WeekendFlag"] = (df["InvoiceDate"].dt.dayofweek >= 5).astype(int)

    # ------------------------------
    # 3) Dimensionality reduction / customer-level reduction
    # ------------------------------
    # Task 1: aggregate transaction-level rows to one row per customer
    customer_df = (
        df.groupby("CustomerID")
        .agg(
            order_count=("InvoiceNo", "nunique"),
            total_quantity=("Quantity", "sum"),
            total_spend=("LineTotal", "sum"),
            avg_unit_price=("UnitPrice", "mean"),
            avg_basket_size=("Quantity", "mean"),
            active_months=("InvoiceMonth", "nunique"),
            shopping_hour_mean=("InvoiceHour", "mean"),
            weekend_purchase_ratio=("WeekendFlag", "mean"),
            dominant_country=("Country", lambda x: x.mode().iat[0] if not x.mode().empty else x.iloc[0]),
            first_purchase=("InvoiceDate", "min"),
            last_purchase=("InvoiceDate", "max"),
        )
        .reset_index()
    )

    # Task 2: convert dates into compact lifecycle features
    reference_date = customer_df["last_purchase"].max()
    customer_df["customer_lifespan_days"] = (
        customer_df["last_purchase"] - customer_df["first_purchase"]
    ).dt.days
    customer_df["recency_days"] = (
        reference_date - customer_df["last_purchase"]
    ).dt.days

    # Task 3: scale numeric features and reduce them using PCA
    features_for_model = [
        "order_count",
        "total_quantity",
        "total_spend",
        "avg_unit_price",
        "avg_basket_size",
        "active_months",
        "shopping_hour_mean",
        "weekend_purchase_ratio",
        "customer_lifespan_days",
        "recency_days",
    ]

    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(customer_df[features_for_model])

    for idx, feature in enumerate(features_for_model):
        customer_df[f"scaled_{feature}"] = scaled_values[:, idx]

    pca = PCA(n_components=3, random_state=42)
    pca_values = pca.fit_transform(scaled_values)
    customer_df["pca_1"] = pca_values[:, 0]
    customer_df["pca_2"] = pca_values[:, 1]
    customer_df["pca_3"] = pca_values[:, 2]

    # ------------------------------
    # 4) Discretization
    # ------------------------------
    # Task 1: spending bands
    customer_df["spend_segment"] = safe_qcut(
        customer_df["total_spend"], 3, ["Low", "Medium", "High"]
    )

    # Task 2: order-frequency bands
    customer_df["frequency_segment"] = safe_qcut(
        customer_df["order_count"], 3, ["Rare", "Regular", "Frequent"]
    )

    # Task 3: recency bands (lower is more recent)
    customer_df["recency_segment"] = safe_qcut(
        customer_df["recency_days"], 3, ["Fresh", "Active", "Dormant"]
    )

    customer_df = customer_df.drop(columns=["first_purchase", "last_purchase"])

    output_path = os.path.join(os.getcwd(), "data_preprocessed.csv")
    customer_df.to_csv(output_path, index=False)

    print("Preprocessing completed successfully.")
    print(f"Saved customer-level dataset to: {output_path}")
    print(f"Final shape: {customer_df.shape}")
    print(f"Explained variance by PCA: {np.round(pca.explained_variance_ratio_, 4).tolist()}")

    subprocess.run([sys.executable, "analytics.py", output_path], check=True)
