# Local Movie Reviews ETL Pipeline

This project is part of my public data engineering portfolio.

As someone transitioning from Accounting into Data Engineering, I wanted to deeply understand how modern systems move from raw events to structured, decision-ready data. This project simulates that real-world flow using a fully containerized, reproducible environment.

At a high level, the system generates movie review events, streams them through Kafka, orchestrates processing with Apache Airflow, and stores structured results in PostgreSQL — all running locally with Docker Compose.

## What This Project Demonstrates (In Simple Terms)

Modern companies constantly collect events (transactions, clicks, logs, ratings) and transform them into structured datasets for reporting and analytics.

This project simulates that process:

- Movie reviews are generated as live events
- Events are streamed reliably through a message broker
- A scheduled workflow processes and aggregates the data
- Clean, structured results are stored in a database

The goal is to demonstrate how raw event data becomes usable business insight.

## Project Scope

This project focuses on ingestion, processing, and aggregation of streaming data.

It does NOT include:

- Real-time dashboards
- Historical ranking comparisons
- Advanced analytics layers

Those extensions are planned for a future project.

## Architecture Overview

This pipeline demonstrates the classic **producer → message broker → orchestrator → sink** pattern:

1. **Python Producer** generates synthetic movie reviews (title, rating 1–10, text, timestamp) and publishes to Kafka
2. **Apache Kafka** (4.1.1 KRaft mode) acts as the reliable message broker
3. **Apache Airflow** (2.10.5) orchestrates the ETL workflow via a DAG:
   - Creates target tables (if needed)
   - Consumes messages from Kafka in batches
   - Inserts raw reviews into PostgreSQL
   - Computes aggregates (avg rating + count per movie) into a stats table
4. **PostgreSQL** (16) serves as the data warehouse with `reviews` and `daily_stats` tables

This architecture mirrors foundational patterns used in production data platforms.

### Data Flow

```
[Python Producer]
    ↓ (publishes)
[Kafka: movie-reviews topic]
    ↓ (Airflow DAG reads)
[Airflow ETL Pipeline]
├─ Create Tables
├─ Consume & Insert Reviews
└─ Compute Aggregates
    ↓ (writes to)
[PostgreSQL Database]
└─ reviews, daily_stats tables
```

## Features

✅ **Fully Automated Setup** - One command to start everything  
✅ **Zero Manual Configuration** - Permissions, connections, and DB migrations handled automatically  
✅ **Production-Ready Patterns** - Proper service dependencies, healthchecks, and initialization  
✅ **Portable** - Runs on any system with Docker and Docker Compose  
✅ **End-to-End Pipeline** - From event generation to data warehousing

## Tech Stack

- **Apache Kafka** 4.1.1 (KRaft mode, single broker)
- **Apache Airflow** 2.10.5 (with PostgreSQL backend)
- **PostgreSQL** 16 (data warehouse and Airflow metadata)
- **Python** 3.12 with kafka-python
- **Docker** & **Docker Compose** for containerization

## Prerequisites

- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **Git** (to clone the repository)

That's it! No manual installations of Kafka, Airflow, or PostgreSQL required.

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Local-Movie-Reviews-ETL-Pipeline.git
cd Local-Movie-Reviews-ETL-Pipeline
```

### 2. Start the Environment

```bash
docker compose up -d
```

This single command will:

- Create and configure all necessary directories with correct permissions
- Start Kafka broker with proper internal/external listeners
- Initialize PostgreSQL database
- Run Airflow database migrations
- Create the `postgres_default` Airflow connection automatically
- Start Airflow webserver and scheduler
- Produce 50 sample movie reviews to Kafka

**Wait ~30 seconds** for all services to become healthy.

### 3. Access Airflow UI

Open your browser to: **http://localhost:8080**

- **Username**: `admin`
- **Password**: `admin`

### 4. Trigger the ETL Pipeline

1. In the Airflow UI, find the DAG: `movie_reviews_etl`
2. Toggle it **ON** (if not already enabled)
3. Click the **▶ Trigger DAG** button
4. Monitor the execution in the **Graph** or **Grid** view

### 5. Verify Results

Check the data in PostgreSQL:

```bash
docker exec -it postgres-db psql -U airflow -d airflow_db
```

Run queries:

```sql
-- View raw reviews
SELECT * FROM reviews LIMIT 10;

-- View aggregated statistics
SELECT * FROM daily_stats ORDER BY review_count DESC;

-- Exit
\q
```

## Project Structure

```
Local-Movie-Reviews-ETL-Pipeline/
├── dags/
│   └── movie_reviews_pipeline.py    # Airflow DAG definition
├── scripts/
│   ├── produce_reviews.py           # Kafka producer script
│   └── wait_for_kafka.py            # Kafka connection health check
├── logs/                             # Airflow logs (auto-created, git-ignored)
├── docker-compose.yml                # Service orchestration
├── Dockerfile                        # Custom Airflow image
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

## Services

| Service           | Port | Description                          |
| ----------------- | ---- | ------------------------------------ |
| Kafka (Internal)  | 9092 | Kafka broker for Docker services     |
| Kafka (External)  | 9094 | Kafka broker for host machine        |
| Airflow Webserver | 8080 | Airflow UI                           |
| PostgreSQL        | 5433 | Database (mapped to avoid conflicts) |

## Producing More Data

To generate additional movie reviews:

```bash
docker compose run --rm producer
```

This will produce another 50 reviews to the `movie-reviews` Kafka topic.

## Stopping the Environment

### Stop all services (keeps data):

```bash
docker compose down
```

### Stop and remove all data (fresh start):

```bash
docker compose down --volumes
```

## Restarting from Scratch

To verify the pipeline works on a fresh system:

```bash
# Clean everything
docker compose down --volumes

# Start fresh (all automations will run again)
docker compose up -d
```

The environment will:

- Recreate volumes
- Set up permissions automatically
- Initialize the database
- Create Airflow connections
- Be ready to use in ~30 seconds

## DAG Details

The `movie_reviews_etl` DAG performs the following tasks:

1. **create_tables**: Creates `reviews` and `daily_stats` tables if they don't exist
2. **consume_and_insert**: Reads messages from Kafka and inserts into `reviews` table
3. **aggregate_stats**: Computes per-movie statistics (avg rating, review count) into `daily_stats`

**Dependencies**: `create_tables` → `consume_and_insert` → `aggregate_stats`

## Troubleshooting

### Services not starting

Check service status:

```bash
docker compose ps
```

View logs for a specific service:

```bash
docker compose logs <service-name>
# Examples: kafka, airflow-webserver, postgres
```

### Kafka connection errors

Ensure Kafka is healthy:

```bash
docker compose logs kafka
```

Wait for the message: `[KafkaServer id=1] started`

### Airflow DAG not visible

1. Check that the `dags/` directory is mounted correctly
2. Restart the scheduler: `docker compose restart airflow-scheduler`

## Development

### Modifying the DAG

Edit `dags/movie_reviews_pipeline.py` and the changes will be picked up automatically (DAG refresh interval is ~30s).

### Adding Python Dependencies

1. Update `requirements.txt`
2. Rebuild the Airflow image:
   ```bash
   docker compose build airflow-common
   docker compose up -d
   ```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built as a learning project to demonstrate:

- Event streaming with Kafka
- Workflow orchestration with Airflow
- Data warehousing patterns
- Docker containerization best practices

## About the Author

Built by **Idris Busari** — a Business Data Transformation Consultant specializing in designing data systems that convert raw operational data into structured, decision-ready insights.

My transition into data engineering is driven by a deep interest in how raw operational data becomes structured insight. I focus on building reproducible, well-architected data systems that reflect real-world production patterns.

I believe strong data engineering begins with mastering fundamentals — event-driven design, workflow orchestration, data modeling, and reproducible environments.

Connect with me:

- LinkedIn: https://www.linkedin.com/in/idris-busari-ohunilu
- X: https://x.com/ohunilu
