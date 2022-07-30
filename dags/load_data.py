import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
from sqlalchemy.types import Integer, Numeric, String


def split_into_chunks(arr, n):
    return [arr[i: i + n] for i in range(0, len(arr), n)]


def read_data():
    df = pd.read_csv('/opt/airflow/data/20181024_d1_0830_0900.csv', skiprows=1, header=None, delimiter="\n")
    series = df[0].str.split(";")
    pd_lines = []

    for line in series:
        old_line = [item.strip() for item in line]
        info_index = 4
        info = old_line[:info_index]
        remaining = old_line[info_index:-1]
        chunks = split_into_chunks(remaining, 6)
        for chunk in chunks:
            record = info + chunk
            pd_lines.append(record)

    new_df = pd.DataFrame(
        pd_lines,
        columns=[
            "track_id",
            "type",
            "traveled_d",
            "avg_speed",
            "lat",
            "lon",
            "speed",
            "lon_acc",
            "lat_acc",
            "time",
        ],
    )

    return new_df.shape


def insert_data():
    pg_hook = PostgresHook(postgres_conn_id="postgres_localhost")
    conn = pg_hook.get_sqlalchemy_engine()

    df = pd.read_csv('/opt/airflow/data/20181024_d1_0830_0900.csv', skiprows=1, header=None, delimiter="\n")
    series = df[0].str.split(";")
    pd_lines = []

    for line in series:
        old_line = [item.strip() for item in line]
        info_index = 4
        info = old_line[:info_index]
        remaining = old_line[info_index:-1]
        chunks = split_into_chunks(remaining, 6)
        for chunk in chunks:
            record = info + chunk
            pd_lines.append(record)

    new_df = pd.DataFrame(
        pd_lines,
        columns=[
            "track_id",
            "type",
            "traveled_d",
            "avg_speed",
            "lat",
            "lon",
            "speed",
            "lon_acc",
            "lat_acc",
            "time",
        ],
    )

    new_df.to_sql(
        "open_traffic",
        con=conn,
        if_exists="replace",
        index=True,
        index_label="id",
        dtype={
            "track_id": Integer(),
            "traveled_d": Numeric(),
            "avg_speed": Numeric(),
            "lat": Numeric(),
            "lon": Numeric(),
            "speed": Numeric(),
            "lon_acc": Numeric(),
            "lat_acc": Numeric(),
            "time": Numeric(),
        },
    )


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
        "load_dag",
        default_args=default_args,
        schedule_interval="0 * * * *",
        catchup=False,
) as dag:
    read_data_op = PythonOperator(
        task_id="read_data", python_callable=read_data
    )
    create_table_op = PostgresOperator(
        task_id="create_table",
        postgres_conn_id="postgres_localhost",
        sql="""
            create table if not exists traffic (
                id serial,
                track_id integer,
                type text,
                traveled_d numeric,
                avg_speed numeric,
                lat numeric,
                lon numeric,
                speed numeric,
                lon_acc numeric,
                lat_acc numeric,
                time numeric
            )
            """,
    )
    load_data_op = PythonOperator(
        task_id="load_data",
        python_callable=insert_data
    )

read_data_op >> create_table_op >> load_data_op