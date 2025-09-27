# Taxi Data Ingestion Pipeline

## Overview
This project implements an end-to-end ingestion pipeline for the NYC Taxi dataset.
It demonstrates how to:

1. Containerize Postgres + PgAdmin with Docker Compose.
2. Ingest raw parquet data into Postgres using a parameterized Python script.
3. Explore and validate data in PgAdmin with SQL queries.

The pipeline is designed as a reproducible template that can be adapted to other datasets.

## Tech stark

1. Docker & Docker Compose – containerization and orchestration
2. Postgres – relational database for storing ingested data
3. PgAdmin – GUI client for SQL queries
4. Python (Pandas,sqlalchemy pyarrow requests psycopg2-binary) – ingestion logic
5. Parquet dataset – NYC Taxi public dataset


## Setup Instructions
1. Clone the repository
```
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

```

2. Start Postgres and PgAdmin
```
bash

docker-compose up -d

```
3. Build the ingestion image

``` bash
docker build -t nyc_taxi_ingest:v001 .

```
4. Run the ingestion pipeline

```
docker run -it \
    --network=nyc-taxi-data_default \
    nyc_taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pgdatabase \
    --port=5432 \      
    --db=ny_taxi_data \
    --table_name=ny_taxi_trips \      
    --url=${URL}

```

## How the pipeline works
1. Docker Compose provisions Postgres + PgAdmin.
2. ny_upload_data.py:
    1. Downloads parquet data from URL.
    2. Reads it in chunks (PyArrow).
    3. Inserts batches into Postgres via SQLAlchemy.
    4. Prints ingestion progress and row counts.
3. PgAdmin is used to query and validate the ingested data.

## Why this matters
In a real-world data engineering workflow, ingestion pipelines are critical because they:
    1. Move data reliably from raw sources into storage.
    2. Enforce schema consistency.
    3. Ensure downstream analytics and ML models have fresh, accurate data.

This project shows how to build such a pipeline with reproducible, containerized components.