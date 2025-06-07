from airflow import DAG
from airflow.operators.python import PythonOperator 
from datetime import datetime

def hello_world():
    print("Airflow funcionando")

with DAG(
    dag_id='mood_etl_dag_test',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False
) as dag:
    hello_task = PythonOperator(
        task_id='say_hello',
        python_callable=hello_world
    )
