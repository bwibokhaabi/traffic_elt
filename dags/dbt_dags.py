from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['daisyokacha9@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    "start_date": datetime(2022, 7, 20, 2, 30, 00),
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    "dbt_dag",
    default_args=default_args,
    schedule_interval="0 * * * *",
    catchup=False,
) as dag:
    dbt_run = BashOperator(
        task_id="dbt_run", bash_command="dbt run --profiles-dir /opt/airflow/dbt --project-dir /opt/airflow/dbt"
    )
    dbt_test = BashOperator(
        task_id="dbt_test", bash_command="dbt test --profiles-dir /opt/airflow/dbt --project-dir /opt/airflow/dbt"
    )
    dbt_doc_gen = BashOperator(
        task_id="dbt_doc_gen", bash_command="dbt docs generate --profiles-dir /opt/airflow/dbt --project-dir "
                                            "/opt/airflow/dbt"
    )

dbt_run >> dbt_test >> dbt_doc_gen