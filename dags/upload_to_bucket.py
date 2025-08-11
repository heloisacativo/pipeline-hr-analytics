from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import datetime, timedelta
import os
import oci

log = LoggingMixin().log

FILE_PATH   = os.getenv("FILE_PATH", "/opt/airflow/data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv")
OBJECT_PREF = os.getenv("OBJECT_PREFIX", "hr")  # prefixo na chave do objeto no bucket

def upload_to_bucket(**_):
    log.info("Starting upload task via SDK OCI...")

    # 1) valida arquivo local
    if not os.path.exists(FILE_PATH):
        raise FileNotFoundError(f"Input file not found: {FILE_PATH}")

    # 2) credenciais/params via env
    bucket  = os.environ["OCI_BUCKET_NAME"]          # defina no .env
    profile = os.getenv("OCI_PROFILE", "DEFAULT")    # defina no .env (opcional)

    # 3) autenticação via ~/.oci/config (dentro do container)
    cfg_path = os.path.expanduser("~/.oci/config")
    config   = oci.config.from_file(cfg_path, profile_name=profile)
    client   = oci.object_storage.ObjectStorageClient(config)
    namespace = client.get_namespace().data

    # 4) nome do objeto com timestamp
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    object_name = f"{OBJECT_PREF}/WA_Attrition_{ts}.csv"

    # 5) upload
    with open(FILE_PATH, "rb") as f:
        resp = client.put_object(namespace, bucket, object_name, f, content_type="text/csv")

    log.info(
        "Uploaded to oci://%s/%s/%s | etag=%s | opc-request-id=%s",
        namespace, bucket, object_name,
        resp.headers.get("etag"), resp.headers.get("opc-request-id")
    )
    return {"namespace": namespace, "bucket": bucket, "object": object_name}

default_args = {
    "owner": "airflow",
    "retries": 0,
    "execution_timeout": timedelta(minutes=5),
}

with DAG(
    dag_id="upload_to_bucket",
    description="Uploads dataset to OCI bucket (SDK OCI)",
    schedule=None,
    start_date=datetime(2025, 8, 10),
    catchup=False,
    is_paused_upon_creation=False,
    default_args=default_args,
    tags=["etl"],
) as dag:
    upload_task = PythonOperator(
        task_id="upload_to_bucket",
        python_callable=upload_to_bucket,
    )
