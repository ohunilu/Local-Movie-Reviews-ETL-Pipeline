from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator 
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import json
from kafka import KafkaConsumer

def consume_and_insert(**context):
    
    consumer = KafkaConsumer(
        'movie-reviews',
        bootstrap_servers='kafka:9092',
        auto_offset_reset='earliest',           # or 'latest' if you only want new
        enable_auto_commit=True,
        group_id='airflow-movie-reviews-group', # helps with offset management
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        max_poll_records=500,                   # limit per poll
        consumer_timeout_ms=10000               # stop after 10s of no new messages
    )

    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

    inserted = 0
    try:
        for message in consumer:
            review = message.value
            postgres_hook.run("""
                INSERT INTO reviews (movie, rating, review_text, review_time)
                VALUES (%s, %s, %s, to_timestamp(%s))
                ON CONFLICT DO NOTHING  -- optional idempotency
            """, parameters=(
                review['movie'],
                review['rating'],
                review['text'],
                review['timestamp']
            ))
            inserted += 1
            if inserted >= 1000:  # safety limit
                break
    finally:
        consumer.close()

    context['ti'].xcom_push(key='inserted_count', value=inserted)
    print(f"Inserted {inserted} reviews")

with DAG(
    dag_id='movie_reviews_etl',
    start_date=datetime(2025, 1, 1),
    schedule='@hourly',
    catchup=False,
    max_active_runs=1
) as dag:

    create_table = SQLExecuteQueryOperator(
        task_id='create_table',
        conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            movie VARCHAR(100),
            rating INT,
            review_text TEXT,
            review_time TIMESTAMP
        );
        """
    )

    ingest = PythonOperator(
        task_id='kafka_to_postgres',
        python_callable=consume_and_insert
    )

    aggregate = SQLExecuteQueryOperator(
        task_id='daily_aggregates',
        conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS daily_stats AS
        SELECT movie, AVG(rating) as avg_rating, COUNT(*) as review_count
        FROM reviews
        GROUP BY movie;
        """
    )

    create_table >> ingest >> aggregate