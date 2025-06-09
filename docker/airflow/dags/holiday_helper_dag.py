from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging



import sys
import os

sys.path.append('/opt/airflow/dags/src/app/utils')
import db_utils
import recommendation
from db_utils import get_latest_mood
from recommendation import get_media_by_mood



def fetch_mood(ti, **kwargs):
    """Recupera o humor mais recente do db e envia 
    via XCom para as próximas tasks
    """
    mood = get_latest_mood()
    logging.info(f"Último humor registrado: {mood}")
    ti.xcom_push(key='mood', value=mood)

def fetch_media(ti, **kwargs):
    """
    Recebe o humor via XCom, busca uma mídia compatível
    e envia o resultado via XCom.
    """
     # mood = ti.xcom_pull(key='mood', task_ids='fetch_mood')
    mood = 'animado'  # mood fixo para teste
    media = get_media_by_mood(mood)
    print(f"Mídia recomendada para o humor '{mood}': {media}")
    ti.xcom_push(key='media', value=media)

default_args = {
    'start_date': datetime(2025, 6, 1),
    'catchup': False,
}

with DAG(
    'holiday_helper_dag',
    default_args=default_args,
    schedule='@daily',
    tags=['holiday'],
) as dag:

    fetch_mood_task = PythonOperator(
        task_id='fetch_mood',
        python_callable=fetch_mood,
    )

    fetch_media_task = PythonOperator(
        task_id='fetch_media',
        python_callable=fetch_media,
    )

    fetch_mood_task >> fetch_media_task
    # fetch_media_task