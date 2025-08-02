# Sydney Transport Pulse – Project Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Solution Architecture](#solution-architecture)
3. [Tech Stack & Services](#tech-stack--services)
4. [Data Sources](#data-sources)
5. [Repository Structure](#repository-structure)
6. [Local Development Environment](#local-development-environment)
7. [Cloud Deployment (AWS reference)](#cloud-deployment-aws-reference)
8. [Data Pipeline Details](#data-pipeline-details)
9. [Data Quality & Testing](#data-quality--testing)
10. [CI/CD Workflow](#cicd-workflow)
11. [Observability & Alerting](#observability--alerting)
12. [Visualisation Layer](#visualisation-layer)
13. [Security & Compliance](#security--compliance)
14. [Cost‑Management Guidelines](#cost-management-guidelines)
15. [Troubleshooting & FAQ](#troubleshooting--faq)
16. [Stretch Goals](#stretch-goals)
17. [References & Further Reading](#references--further-reading)

---

## Project Overview

**Sydney Transport Pulse** is a real‑time data‑lakehouse that ingests live GTFS‑Realtime GPS pings from Transport for NSW (TfNSW), enriches them with static timetable data, and surfaces live on‑time‑performance dashboards.
The project is designed to showcase *every core competency* sought in 2025 junior data‑engineering roles:

| Competency                       | Demonstrated By                                        |
| -------------------------------- | ------------------------------------------------------ |
| Cloud object storage & lakehouse | Iceberg tables on S3 (or MinIO for local)              |
| Streaming ingestion              | Kafka → Spark Structured Streaming                     |
| Batch ELT & modelling            | dbt transformation from **bronze → silver → gold**     |
| Orchestration                    | Apache Airflow DAGs                                    |
| IaC & CI/CD                      | Terraform modules + GitHub Actions pipeline            |
| Data quality                     | Great Expectations tests & Airflow fail‑fast gates     |
| Observability                    | Prometheus metrics + Grafana dashboards + Slack alerts |
| Visualisation                    | Apache Superset interactive dashboards                 |

> **Elevator pitch (30 s):** “How late is the 891 bus to UNSW?  My pipeline streams every vehicle GPS ping (\~3 M/day), builds Iceberg fact tables in near‑real‑time, validates data quality, and publishes an on‑time‑performance dashboard – all infra defined in Terraform, tested in GitHub Actions, and monitored in Grafana.”

---

## Solution Architecture

```
+------------------+        +------------------+        +------------------+
|  TfNSW API       |  -->   |  Kafka Topic     |  -->   |  Spark Structured |
|  (GTFS‑Realtime) |  1     |  bus_positions   |  2     |  Streaming Job    |
+------------------+        +------------------+        +------------------+
         |                                                         |
         |3                                                        |4
         v                                                         v
+------------------+                                       +------------------+
|  Iceberg Bronze  |  --(Airflow)-->  Iceberg Silver  -->  |  Iceberg Gold    |
|  (Raw JSON)      |                    (Clean)           |  (fact/dim)       |
+------------------+                                       +------------------+
         |                                                         |
         |5                                                        |6
         v                                                         v
+------------------+                                       +------------------+
| Great Expectations|                                     | Superset / Snowfl|
| Validation        |                                     |  queries & charts |
+------------------+                                       +------------------+
         |                                                         |
         +-----------+--------------------+-------------------------+
                     |                    |
               Prometheus <‑‑ metrics ‑‑> Grafana  (alerts to Slack)
```

**Legend:**

1. Python `producer.py` polls the TfNSW VehiclePosition gRPC endpoint every 10 s.
2. Raw JSON pushed to Kafka topic **`bus_positions`**.
3. Spark Structured Streaming writes each micro‑batch to Iceberg *bronze* table on S3.
4. Hourly Airflow DAG triggers Spark batch job to cleanse/join GTFS static → *silver* table.
5. Airflow task runs Great Expectations; fails pipeline if <95 % rows pass.
6. dbt **`run`** and **`test`** create star‑schema (*gold*) in Snowflake, queried by Superset.


---

## Tech Stack & Services

| Layer               | Local Dev (Docker Compose) | Cloud (AWS reference)                                                         |
| ------------------- | -------------------------- | ----------------------------------------------------------------------------- |
| Object Storage      | MinIO                      | Amazon S3                                                                     |
| Streaming           | Kafka + Zookeeper          | Amazon MSK (Kafka)                                                            |
| Compute (Streaming) | Spark 3.5 / PySpark        | EMR Serverless or Glue 4.0                                                    |
| Compute (Batch)     | Spark on Docker            | AWS Glue Jobs                                                                 |
| Orchestration       | Apache Airflow 2.9         | MWAA (Managed Airflow)                                                        |
| Lakehouse Format    | Apache Iceberg 1.5         | Iceberg on S3                                                                 |
| Modelling           | dbt Core 1.8               | dbt Core on EC2 (CI) or dbt Cloud                                             |
| Data Quality        | Great Expectations 0.18    | Same                                                                          |
| Monitoring          | Prometheus + Grafana       | Prometheus OSS on EC2 / Amazon Managed Service for Prometheus + Grafana Cloud |
| CI/CD               | GitHub Actions             | GitHub Actions (self‑hosted runner optional)                                  |
| IaC                 | Terraform 1.7              | Terraform + S3 backend + AWS IAM                                              |
| BI / Viz            | Superset 4.0               | Superset on ECS Fargate                                                       |

---

## Data Sources

| Feed                                | Format          | Frequency      | Endpoint                                                   |
| ----------------------------------- | --------------- | -------------- | ---------------------------------------------------------- |
| **GTFS‑Realtime Vehicle Positions** | Protobuf / gRPC | Every 10 s     | `https://api.transport.nsw.gov.au/v1/gtfs/vehiclepos`      |
| **GTFS Static Timetables**          | Zip (CSV)       | Daily snapshot | `https://api.transport.nsw.gov.au/v1/gtfs/schedule/{date}` |

API access requires registering an app key with [TfNSW Open Data](https://opendata.transport.nsw.gov.au/).  Store the key as `TFNSW_API_KEY`.

---

## Repository Structure

```
├── docker-compose.yml
├── .env.example
├── ingest/
│   ├── producer.py            # GTFS‑Realtime → Kafka
│   └── requirements.txt
├── spark_jobs/
│   ├── bronze_stream.py       # Structured Streaming
│   └── silver_batch.py        # Batch cleanse & join
├── airflow/
│   └── dags/pipeline.py       # DAG definition (bronze→silver→dbt→quality)
├── dbt/
│   ├── models/
│   │   ├── dim_route.sql
│   │   └── fact_trip_punctuality.sql
│   └── tests/
├── great_expectations/
│   └── ...
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/dashboards/
├── iac/
│   └── terraform/*            # S3, MSK, EMR, MWAA modules
├── .github/workflows/
│   ├── ci.yml                 # lint + unit tests
│   └── deploy.yml             # Terraform plan/apply + dbt docs
└── docs/
    └── demo_script.md
```

---

## Local Development Environment

1. **Clone repo & copy env file**

   ```bash
   git clone https://github.com/<your‑user>/sydney‑transport‑pulse.git
   cd sydney‑transport‑pulse
   cp .env.example .env   # add TFNSW_API_KEY & AWS creds (localstack optional)
   ```
2. **Install Python dependencies**

   ```bash
   pip install -r ingest/requirements.txt
   ```
3. **Launch stack**

   Start all services (Kafka, Spark, Airflow, MinIO, Prometheus, Grafana and Superset) with Docker Compose:

   ```bash
   docker compose up -d
   # Wait about 30s for Airflow on http://localhost:8080 and Superset on http://localhost:8088
   ```
4. **Seed GTFS static** (daily job)

   ```bash
   make fetch_gtfs_static          # downloads & pushes to MinIO s3://stp/gtfs_static/
   # DATE=20240101 make fetch_gtfs_static  # optional override
   ```
5. **Start streaming**

   Launch the Python producer which polls the TfNSW API and publishes messages to the `bus_positions` topic:

   ```bash
   python ingest/producer.py   # or docker exec kafka-producer
   ```
6. **Trigger DAG manually**

   1. Open Airflow → `pipeline_gtfs_bus` DAG → *Trigger Run*.
   2. Watch tasks: `bronze_stream`, `silver_batch`, `dbt_run`, `ge_validate`.
7. **Explore data**

   ```sql
   -- inside Superset SQL Lab
   SELECT route_id, COUNT(*) AS trips, AVG(delay_min) AS avg_delay
   FROM fact_trip_punctuality
   WHERE service_date = CURRENT_DATE
   GROUP BY route_id
   ORDER BY avg_delay DESC;
   ```

### Environment variables

| Name                                          | Purpose                 | Example                                |
| --------------------------------------------- | ----------------------- | -------------------------------------- |
| `TFNSW_API_KEY`                               | Auth token for GTFS API | `abcd1234xyz`                          |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Terraform + EMR         | `AKIA…`                                |
| `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`     | Local S3 creds          | `minioadmin`                           |
| `SLACK_WEBHOOK_URL`                           | Alert channel           | `https://hooks.slack.com/services/...` |

---

## Cloud Deployment (AWS reference)

> **Goal:** replicate local topology using managed AWS services via Terraform.

### High‑level steps

1. `cd iac/terraform && terraform init`
2. `terraform plan ‑var-file="prod.tfvars"`
3. `terraform apply` (creates S3 bucket `stp‑lake‑prod`, MSK cluster, EMR Serverless workspace, MWAA env, IAM roles).
4. Push Airflow DAG & plugins to MWAA S3 bucket.
5. Trigger MWAA DAG to start streaming job on EMR Serverless.


### Terraform state‑management

* **Backend:** S3 bucket `stp‑tfstate` + DynamoDB table for locks.
* Use `AWS_PROFILE=stp‑prod` or `AWS_ROLE` in CI for least‑privilege.

### Networking

| Service        | VPC                   | Public/Private           |
| -------------- | --------------------- | ------------------------ |
| MSK brokers    | `vpc‑stp`             | Private subnets with NAT |
| EMR Serverless | same VPC              | Private                  |
| MWAA           | same VPC              | Private + ALB            |
| Superset (ECS) | Public subnet via ALB | Public URL (optional)    |

See `iac/terraform/README.md` for full variable docs.

---

## Data Pipeline Details

### Bronze Layer – Raw

* Spark Structured Streaming micro‑batches (trigger once/10 s).
* Schema evolves via Iceberg’s **schema‑on‑read**; partitioned by `service_date`.

### Silver Layer – Cleansed

* Batch job every 15 min.
* Deduplicates on `(trip_id, timestamp)`, validates geo boundaries, joins to timetable (`route_id`).
* Columns: `route_id`, `trip_id`, `vehicle_id`, `event_time`, `delay_sec`, …

### Gold Layer – Analytics

* dbt incremental models (partition by `service_date`).
* `fact_trip_punctuality` (one row per stop arrival).
* `dim_route` (route metadata).
* Materialised in Snowflake for interactive BI.

### Orchestration

```
bronze_stream (SparkStreaming, always‑on)
   ↓ hourly trigger
silver_batch  ->  dbt_run  ->  ge_validate  ->  superset_refresh
```

* DAG retries 2×, exponential back‑off.
* Failure alerts via Slack webhook.

---

## Data Quality & Testing

| Tool                                                  | Tests                            |
| ----------------------------------------------------- | -------------------------------- |
| **Great Expectations**                                | • Null & range checks on lat/lon |
| • `delay_sec >= 0`                                    |                                  |
| • Row count vs expectation (≥90 % of scheduled trips) |                                  |
| **dbt tests**                                         | • `not_null` on PKs              |
| • `unique` on `dim_route.route_id`                    |                                  |
| • Custom SQL test: punctuality in \[‑10, +120] min    |                                  |

Failing any GE checkpoint marks Airflow task **failed**, halting DAG.

### Running validations locally

Execute the checkpoint using the Great Expectations CLI:

```bash
great_expectations -c great_expectations/great_expectations.yml checkpoint run stp_bus
```

---

## CI/CD Workflow

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r ingest/requirements.txt
      - run: flake8 ingest spark_jobs
      - name: dbt run & test
        run: |
          cd dbt && dbt deps && dbt run -m +fact_trip_punctuality --profiles-dir profiles && dbt test --profiles-dir profiles
  terraform:
    if: github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest
    environment: prod
    steps:
      - uses: hashicorp/setup-terraform@v3
      - run: terraform fmt -check
      - run: terraform init
      - run: terraform plan -out=tfplan
      - run: terraform apply -input=false tfplan
```

* **dbt Docs Publish:** post‐deploy step uploads site to S3 and invalidates CloudFront.

---

## Observability & Alerting

* **Prometheus exporters**

  * Spark (JMX) → scrape `/metrics` via `jmx_prometheus_javaagent`.
  * Airflow metrics exported via built‑in `/admin/metrics` (2.9+).
  * Custom exporter for Kafka consumer lag.
* **Grafana dashboards**

  * *Pipeline Health* – DAG duration, task success ratio.
  * *Bus Delay Heatmap* – real‑time average delay by route/hour.
  * *Infrastructure* – MSK broker CPU, EMR cost.
  
  Example JSON exports are provided under `monitoring/grafana/dashboards/`.
  To load them into Grafana:
  1. Open the Grafana web UI.
  2. Navigate to **Create → Import**.
  3. Upload any dashboard JSON file from that directory and confirm.
* **Alerts**

  * Slack alert if `ge_validate` fails.
  * PagerDuty webhook on consumer lag > 2 min.

---

## Visualisation Layer

* Superset on `http://localhost:8088` (admin/admin).
* Key charts:

  1. **Map** – real‑time vehicle positions (point geo, auto‑refresh 15 s).
  2. **Delay by Hour** – heatmap of average delay minutes across hours × routes.
  3. **On‑time % trend** – line chart by day.
* Dashboards exported under `superset/`.
  To import the JSON files:
  1. Log in as an admin user.
  2. Go to **Settings → Import Dashboards**.
  3. Upload any file from `superset/` and confirm.

---

## Security & Compliance

| Concern             | Mitigation                                                         |
| ------------------- | ------------------------------------------------------------------ |
| API key leakage     | `.env` not committed; secrets in GitHub + SSM Parameter Store      |
| Data privacy        | Only public GPS data, no personal information.                     |
| IAM least privilege | Terraform IAM roles: EMR runtime role limited to S3 bucket prefix. |
| Network ingress     | MSK/Airflow in private subnets; Superset public but read‑only.     |
| Credential rotation | Use AWS Secrets Manager rotation for Slack/webhooks.               |

---

## Cost‑Management Guidelines

* **MSK tier:** use `kafka.t3.small` brokers (≈AUD 0.13/hr each) for test env.
* **EMR Serverless:** configure pre‑initialised workers = 0, scaling between 0–4.
* **S3 lifecycle:** move bronze to Glacier after 30 days.
* **Grafana Cloud free tier** or use OSS on EC2 t4g.micro.

Typical monthly dev‑env cost < **AUD 50** when idle (\~10 GB storage, low MSK usage).


---

## Troubleshooting & FAQ

| Issue                                     | Fix                                                                                               |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `producer.py` 403                         | TfNSW API key invalid → regenerate key, export `TFNSW_API_KEY`.                                   |
| Spark job exits w/ *NoClassDefFoundError* | Ensure `--packages` includes `org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0`.           |
| Airflow cannot reach MinIO                | Update `.env`: `MINIO_ENDPOINT=http://minio:9000` and add network `airflow` in compose overrides. |
| Superset blank map tiles                  | Under *Settings → Mapbox API* add your token or switch to OpenStreet basemap plugin.              |

---

## Stretch Goals

* **Streaming ML:** PyFlink job for anomaly detection on delay spikes.
* **Athena Iceberg query:** expose data to analysts without Snowflake licence.
* **OpenTelemetry trace export:** unify Spark + Airflow + Superset traces.
* **Autoscaling demo:** Karpenter on EKS for Spark pods.

---

## References & Further Reading

* TfNSW Open Data docs – [https://opendata.transport.nsw.gov.au/](https://opendata.transport.nsw.gov.au/)
* Iceberg quick‑start – [https://iceberg.apache.org/docs/latest/](https://iceberg.apache.org/docs/latest/)
* Great Expectations deployment patterns – [https://docs.greatexpectations.io/](https://docs.greatexpectations.io/)
* AWS EMR Serverless best practices – 2025 white‑paper
* dbt “Definitive Guide to Star Schemas” – dbt Labs 2023



