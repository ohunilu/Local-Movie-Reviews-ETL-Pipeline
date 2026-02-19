from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator 
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import json
import os
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
    
    # Load SQL from external file
    dag_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(dag_dir, 'sql', 'insert_review.sql')
    with open(sql_path, 'r') as f:
        insert_sql = f.read()

    inserted = 0
    try:
        for message in consumer:
            review = message.value
            postgres_hook.run(insert_sql, parameters=(
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
    max_active_runs=1,
    template_searchpath=[os.path.dirname(os.path.abspath(__file__)) + '/sql']
) as dag:

    create_table = SQLExecuteQueryOperator(
        task_id='create_table',
        conn_id='postgres_default',
        sql='create_reviews_table.sql'
    )

    ingest = PythonOperator(
        task_id='kafka_to_postgres',
        python_callable=consume_and_insert
    )

    aggregate = SQLExecuteQueryOperator(
        task_id='daily_aggregates',
        conn_id='postgres_default',
        sql='daily_aggregates.sql'
    )

    create_table >> ingest >> aggregate