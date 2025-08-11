from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import kagglehub
import zipfile
import os
import shutil

BASE_DIR = "/opt/airflow/data"
RAW_DIR = os.path.join(BASE_DIR, "raw")

def extract_dataset(**kwargs):
    path = kagglehub.dataset_download("pavansubhasht/ibm-hr-analytics-attrition-dataset")
    print("Path to dataset files:", path)

    os.makedirs(RAW_DIR, exist_ok=True)

    files = os.listdir(path)
    print(f"Arquivos baixados: {files}")

    for fname in files:
        src = os.path.join(path, fname)

        if fname.lower().endswith(".zip"):
            with zipfile.ZipFile(src, "r") as zf:
                zf.extractall(RAW_DIR)
            print(f"Arquivo {fname} descompactado em {RAW_DIR}")
        else:
            dst = os.path.join(RAW_DIR, fname)
            try:
                # Evita erro de metadados em bind mounts do Windows
                shutil.copy(src, dst)        # <- use copy (não copy2)
            except PermissionError:
                # fallback defensivo (raramente necessário após usar copy)
                with open(src, "rb") as r, open(dst, "wb") as w:
                    w.write(r.read())
            print(f"Arquivo {fname} copiado para {RAW_DIR}")

    expected = os.path.join(RAW_DIR, "WA_Fn-UseC_-HR-Employee-Attrition.csv")
    print("Dataset disponível em", RAW_DIR, "| arquivo esperado existe?", os.path.exists(expected))

with DAG(
    dag_id="extract_dataset",
    description="Downloads and extracts HR Analytics dataset",
    schedule_interval=None,
    start_date=datetime(2025, 8, 10),
    catchup=False,
) as dag:
    extract_task = PythonOperator(
        task_id="extract_dataset",
        python_callable=extract_dataset,
    )
