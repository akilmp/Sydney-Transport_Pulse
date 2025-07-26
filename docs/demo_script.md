# Demo Script

This walkthrough demonstrates how to run the full Sydney Transport Pulse stack locally, trigger the Airflow workflow and explore the dashboards in Superset.

1. **Clone the repository and prepare the environment**
   ```bash
   git clone https://github.com/<your-user>/sydney-transport-pulse.git
   cd sydney-transport-pulse
   cp .env.example .env    # add your TFNSW_API_KEY
   pip install -r ingest/requirements.txt
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker compose up -d
   ```
   - Airflow web UI: <http://localhost:8080> (admin/airflow)
   - Superset: <http://localhost:8088> (admin/admin)
   Wait 30 s for containers to initialise.

3. **Load the GTFS static schedule**
   ```bash
   make fetch_gtfs_static
   ```
   This downloads the daily timetable files and uploads them to MinIO.

4. **Begin streaming real-time data**
   ```bash
   python ingest/producer.py
   ```
   The script polls the TfNSW API every 10 s and publishes messages to the `bus_positions` topic in Kafka.

5. **Trigger the Airflow DAG**
   1. Open the Airflow UI at `http://localhost:8080`.
   2. Find the **`pipeline_gtfs_bus`** DAG.
   3. Click **Trigger DAG** and watch the tasks (`bronze_stream`, `silver_batch`, `dbt_run`, `ge_validate`) complete.

6. **Explore dashboards in Superset**
   1. Navigate to `http://localhost:8088` and log in.
   2. Import the JSON files from the `superset/` directory if prompted.
   3. Open the *Vehicle Locations Map* or *Route Delay Dashboard* to see live data.

7. **Optional SQL query**
   Open Superset → SQL Lab and run:
   ```sql
   SELECT route_id, AVG(delay_min) AS avg_delay
   FROM fact_trip_punctuality
   WHERE service_date = CURRENT_DATE
   GROUP BY route_id
   ORDER BY avg_delay DESC;
   ```

Following these steps will demonstrate the entire pipeline—from ingestion to analytics dashboards—running on your local machine.
