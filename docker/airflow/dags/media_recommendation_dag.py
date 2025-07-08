from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import json

import sys
import os

sys.path.append('/opt/airflow/dags/src/shared')
import spotify_utils
from spotify_utils import get_spotify_token, get_spotify_genres, search_playlists_by_genres
import wired_today 
from wired_today import random_wired_articles_today


sys.path.append('/opt/airflow/dags/src/app/utils')
import import_letterboxd
from import_letterboxd import import_watchlist

DATA_DIR = "data/"

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 0,
}

with DAG(
    dag_id="media_recommendation_dag",
    description="Gera recomendações de mídia: filmes, Spotify, Wired e checklist de clima",
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=["holiday", "media"],
) as dag:

    def generate_playlist_task():
        genres = get_spotify_genres()  # sua função para listar gêneros desejados
        token = get_spotify_token()
        playlists = search_playlists_by_genres(token, genres)
        with open(os.path.join(DATA_DIR, "spotify_playlists.json"), "w", encoding="utf-8") as f:
            json.dump(playlists, f, ensure_ascii=False, indent=2)

    def generate_wired_news_task():
        articles = random_wired_articles_today()
        with open(os.path.join(DATA_DIR, "wired_news.json"), "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)



    def import_letterboxd_task():
        csv_path = "/opt/airflow/data/letterboxd_watchlist.csv"
        import_watchlist(csv_path)

    t1 = PythonOperator(task_id="recommend_playlists", python_callable=generate_playlist_task)
    t2 = PythonOperator(task_id="fetch_wired_news", python_callable=generate_wired_news_task)
    t3 = PythonOperator(task_id="import_watchlist", python_callable=import_letterboxd_task)

    [t1, t2] >> t3  # Executa tudo antes de importar os filmes