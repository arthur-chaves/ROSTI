from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Imports das funções do prj (ideias)
# from app.utils.recommendation import get_media_by_mood
# from shared.fetch_transport import get_transport_data, parse_transport_response
# from app.utils.db_utils import insert_mood, get_connection

default_args = {
    'owner': 'holiday_helper',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def buscar_humor():
    # Função stub para buscar humor no banco
    pass

def buscar_sugestao_midia():
    # Função stub para buscar sugestão de mídia
    pass

def buscar_transporte():
    # Função stub para buscar dados de transporte
    pass

def salvar_log():
    # Função stub para salvar log
    pass

with DAG(
    'holiday_helper_dag',
    default_args=default_args,
    description='DAG main para o prj Holiday Helper',
    schedule='@daily',
    catchup=False,
    tags=['holiday'],
) as dag:

    task_buscar_humor = PythonOperator(
        task_id='buscar_humor',
        python_callable=buscar_humor,
    )

    task_buscar_sugestao_midia = PythonOperator(
        task_id='buscar_sugestao_midia',
        python_callable=buscar_sugestao_midia,
    )

    task_buscar_transporte = PythonOperator(
        task_id='buscar_transporte',
        python_callable=buscar_transporte,
    )

    task_salvar_log = PythonOperator(
        task_id='salvar_log',
        python_callable=salvar_log,
    )

    # Definindo a ordem das tasks
    task_buscar_humor >> task_buscar_sugestao_midia >> task_buscar_transporte >> task_salvar_log
