from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta

# Define default arguments
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'execution_timeout': timedelta(minutes=5)
}

with DAG(
    'etl_master',
    default_args=default_args,
    description='Master ETL Pipeline',
    schedule_interval=None,
    start_date=datetime(2025, 8, 10),
    catchup=False,
    tags=['etl']
) as dag:

    trigger_extract = TriggerDagRunOperator(
        task_id='trigger_extract',
        trigger_dag_id='extract_dataset',
        wait_for_completion=True,
        poke_interval=30,
        failed_states=['failed']  # Removed 'skipped' as it's not a valid state
    )

    trigger_upload = TriggerDagRunOperator(
        task_id='trigger_upload',
        trigger_dag_id='upload_to_bucket',
        conf={
            'source': 'etl_master',
            'file_path': '/opt/airflow/data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv'
        },
        wait_for_completion=True,
        poke_interval=30,
        failed_states=['failed']  # Removed 'skipped' as it's not a valid state
    )

    trigger_bronze = TriggerDagRunOperator(
        task_id='trigger_bronze',
        trigger_dag_id='transform_bronze',
        wait_for_completion=True,
        poke_interval=30
    )

    trigger_gold = TriggerDagRunOperator(
        task_id='trigger_gold',
        trigger_dag_id='transform_gold',
        wait_for_completion=True,
        poke_interval=30
    )

    # Set task dependencies
    trigger_extract >> trigger_upload >> trigger_bronze >> trigger_gold