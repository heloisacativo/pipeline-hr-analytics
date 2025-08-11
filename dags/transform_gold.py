from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import os

def transform_to_gold(**context):
    try:
        # Read from bronze
        df = pd.read_parquet('/opt/airflow/data/bronze/hr_data.parquet')
        
        # Convert Attrition to numeric (Yes=1, No=0)
        df['Attrition'] = (df['Attrition'] == 'Yes').astype(int)
        
        # Calculate metrics
        attrition_by_dept = df.groupby('Department').agg({
            'Attrition': ['count', 'mean'],
            'MonthlyIncome': 'mean'
        }).round(2)
        
        # Rename columns for clarity
        attrition_by_dept.columns = [
            'TotalEmployees',
            'AttritionRate',
            'AvgMonthlyIncome'
        ]
        attrition_by_dept = attrition_by_dept.reset_index()
        
        # Save as CSV for Power BI
        output_path = '/opt/airflow/data/gold/'
        os.makedirs(output_path, exist_ok=True)
        csv_path = f"{output_path}/attrition_metrics.csv"
        attrition_by_dept.to_csv(csv_path, index=False)
        print(f"Saved metrics to CSV: {csv_path}")
        
    except Exception as e:
        print(f"Error in gold transformation: {str(e)}")
        raise e

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'transform_gold',
    default_args=default_args,
    description='Transform data to gold metrics',
    schedule_interval=None,
    start_date=datetime(2025, 8, 10),
    catchup=False,
    tags=['etl', 'gold']
) as dag:
    
    gold_task = PythonOperator(
        task_id='transform_gold',
        python_callable=transform_to_gold
    )