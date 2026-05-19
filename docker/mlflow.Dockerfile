# syntax=docker/dockerfile:1.7
FROM ghcr.io/mlflow/mlflow:v3.12.0

RUN pip install --no-cache-dir psycopg2-binary==2.9.10
