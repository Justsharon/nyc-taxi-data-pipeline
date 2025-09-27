#!/usr/bin/env python
# eda.py
import pandas as pd

df = pd.read_parquet("yellow_tripdata_2025-01.parquet")

print(df.shape)
print(df.head())
print(df.info())
print(df.describe())
print(df.dtypes)

print(df["VendorID"].value_counts())
print(df["tpep_pickup_datetime"].min(), df["tpep_pickup_datetime"].max())
print(df["tpep_dropoff_datetime"].min(), df["tpep_dropoff_datetime"].max())
print(df["passenger_count"].value_counts().sort_index())
print(df["trip_distance"].describe())
print(df["RatecodeID"].value_counts())
print(df["store_and_fwd_flag"].value_counts())
print(df["PULocationID"].nunique(), df["DOLocationID"].nunique())
print(df["payment_type"].value_counts())
fare_cols = ["fare_amount", "extra", "mta_tax", "tip_amount", "tolls_amount",
             "improvement_surcharge", "total_amount", "congestion_surcharge",
             "Airport_fee", "cbd_congestion_fee"]

print(df[fare_cols].describe().T)
