from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "pipeline_gtfs_bus",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
)

bronze_stream = BashOperator(
    task_id="bronze_stream",
    bash_command="spark-submit /opt/bitnami/spark/jobs/bronze_stream.py",
    dag=dag,
)

silver_batch = BashOperator(
    task_id="silver_batch",
    bash_command="spark-submit /opt/bitnami/spark/jobs/silver_batch.py",
    dag=dag,
)

dbt_run = BashOperator(
    task_id="dbt_run",
    bash_command="cd /opt/airflow/dbt && dbt deps && dbt run && dbt test",
    dag=dag,
)

ge_validate = BashOperator(
    task_id="ge_validate",
    bash_command="great_expectations checkpoint run stp_bus",
    dag=dag,
)

bronze_stream >> silver_batch >> dbt_run >> ge_validate
