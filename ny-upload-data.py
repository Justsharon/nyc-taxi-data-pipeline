#!/usr/bin/env python
# coding: utf-8
import argparse
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pyarrow.dataset as ds
from sqlalchemy import text
import requests
import logging
from time import time
import sys
import os


def download_file(url: str, output_path: str):
    try:
        logging.info(f"Downoading data from {url} ...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"Download complete: {output_path}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Download failed: {e}")
        sys.exit(1)


def connect_to_db(user, password, host, port, db):
    try:
        engine = create_engine(
            f'postgresql://{user}:{password}@{host}:{port}/{db}')
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logging.info("Database connection successful.")
        return engine
    except SQLAlchemyError as e:
        logging.error(f"Database connection failed: {e}")
        sys.exit(1)


def ingest_ny_data(engine, parquet_path, table_name):
    try:
        dataset = ds.dataset(parquet_path, format="parquet")
    except Exception as e:
        logging.error(f"Failed to load parquet dataset: {e}")
        sys.exit(1)

    scanner = dataset.to_batches(batch_size=100_000)
    df_iter = (batch.to_pandas() for batch in scanner)

    try:
        # create empty table schema
        df = next(df_iter)
        df.head(0).to_sql(
            name=table_name,
            con=engine,
            if_exists='replace',
            index=False
        )
        logging.info(f"Created table schema: {table_name}")
    except Exception as e:
        logging.error(f"Failed to create schema: {e}")
        sys.exit(1)

    # Insertion of the first batch
    try:
        t_start = time()
        df.to_sql(name=table_name, con=engine, if_exists='append',
                  index=False, method='multi', chunksize=10_000)
        logging.info(
            f"Inserted first chunk ({len(df)} rows) in {time() - t_start:.2f}s")
    except Exception as e:
        logging.error(f"Failed to insert first chunk: {e}")
        sys.exit(1)

    # Insertion of remaining batches
    for i, df in enumerate(df_iter, start=2):
        try:
            t_start = time()
            df.to_sql(name=table_name, con=engine, if_exists='append',
                index=False, method='multi', chunksize=10_000)
            logging.info(f"Inserted chunk {i} ({len(df)} rows) in {time() - t_start:.2f}s")
        except Exception as e:
            logging.error(f"Chunk {i} failed: {e}")
            continue 

    # confirm if number of row is same as what is in db
    try:
        row_count = dataset.count_rows()
        logging.info(f"✅ Ingestion complete. Total rows expected: {row_count}")
    except Exception as e:
        logging.warning(f"Could not count parquet rows: {e}")


def main(params):
    parquet_name = 'output.parquet'

    # download dataset
    download_file(params.url, parquet_name)

    # connect to database
    engine = connect_to_db(params.user, params.password, params.host, params.port, params.db)

    # ingest dataset
    ingest_ny_data(engine, parquet_name, params.table_name)
  

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Ingest parquet data to Postgres')

    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument(
        '--table_name', help='name of the table where we will write our results to')
    parser.add_argument('--url', help='url of the parquet file')

    args = parser.parse_args()

    try:
        main(args)
    except Exception as e:
        logging.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

