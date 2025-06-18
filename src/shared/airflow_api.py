import requests
from datetime import datetime, timezone

AIRFLOW_BASE_URL = "http://host.docker.internal:8080"
USERNAME = "airflow"
PASSWORD = "airflow"

def get_jwt_token():
    url = f"{AIRFLOW_BASE_URL}/auth/token"
    payload = {"username": USERNAME, "password": PASSWORD}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json().get("access_token")

def trigger_dag(dag_id: str, token: str):
    url = f"{AIRFLOW_BASE_URL}/api/v2/dags/{dag_id}/dagRuns"
    headers = {"Authorization": f"Bearer {token}"}
    logical_date = datetime.now(timezone.utc).isoformat()
    payload = {"logical_date": logical_date}
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.status_code, resp.text
