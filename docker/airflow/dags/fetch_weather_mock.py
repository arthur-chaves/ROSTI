from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
import os

sys.path.append('/opt/airflow/dags/src/app/utils')
from db_utils import get_connection

# Função que insere um clima simulado no banco
def insert_mock_weather():
    # Dados de clima simulados
    temp_celsius = 24.5
    condition = "Ensolarado"
    timestamp = datetime.now().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO weather_raw (temperature_celsius, condition, timestamp)
        VALUES (%s, %s, %s)
    """, (temp_celsius, condition, timestamp))
    conn.commit()
    conn.close()

# Define a DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

with DAG(
    dag_id='dag_fetch_weather_mock',
    default_args=default_args,
    schedule=None,  # Só manual por enquanto
    catchup=False,
    tags=['holiday', 'weather'],
) as dag:

    fetch_weather = PythonOperator(
        task_id='insert_mock_weather',
        python_callable=insert_mock_weather,
    )

    fetch_weather
