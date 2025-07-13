from airflow import DAG
from airflow.operators.python import PythonOperator
import datetime
from dotenv import load_dotenv
import os
import sys
import json
sys.path.append('/opt/airflow/dags/src')

sys.path.append('/opt/airflow/dags/src/app/utils')
from db_utils import get_connection

sys.path.append('/opt/airflow/dags/src/shared')
import weather_utils 
from weather_utils import get_daily_forecast
import checklist 
from checklist import generate_checklist
import lake_utils 
from lake_utils import get_all_spots, get_lake_temperature_today
import fetch_transport 
from fetch_transport import get_swim_spots, get_transport_data, parse_transport_response, insert_transport, generate_maps_link
import spotify_utils
from spotify_utils import get_latest_episodes_for_all_podcasts

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
USER_CITY = os.getenv("USER_CITY")
LATITUDE = float(os.getenv("user_lat"))
LONGITUDE = float(os.getenv("user_lng"))

import pendulum

local_tz = pendulum.timezone("Europe/Rome")
with DAG(
    dag_id="lake_weather_transport_dag",
    start_date=datetime.datetime(2025, 7, 9, tzinfo=local_tz),
    catchup=False,
    schedule="0 8 * * *",
    tags=['holiday', 'weather'],
    description="Processes weather, checklist, lake water temperature, podcasts and transit data"
) as dag:

    def task_fetch_weather_forecast(**context):
        forecast = get_daily_forecast(GOOGLE_API_KEY, LATITUDE, LONGITUDE)
        with open("/opt/airflow/dags/src/data/output/weather.json", "w") as f:
            json.dump(forecast, f)
        context["ti"].xcom_push(key="forecast_data", value=forecast)

    def task_generate_checklist(**context):
        forecast_data = context["ti"].xcom_pull(task_ids="fetch_weather_forecast", key="forecast_data")
        if forecast_data is None:
            raise ValueError("Check previous task")

        mensagem, checklist_items = generate_checklist(forecast_data)
        checklist_output = {
        "mensagem": mensagem,
        "itens": checklist_items
        }
        with open("/opt/airflow/dags/src/data/output/checklist.json", "w") as f:
            json.dump(checklist_output, f)


    def task_fetch_lake_temperatures(**context):
        spots = get_all_spots()
        results = []
        for name, lake, lat, lng in spots:
            temp, status = get_lake_temperature_today(lake, lat, lng)
            results.append({"name": name, "lake": lake, "temp": temp, "status": status})
        context["ti"].xcom_push(key="lake_temperatures", value=results)
        with open("/opt/airflow/dags/src/data/output/lake_temperatures.json", "w") as f:
            json.dump(results, f)

    def task_fetch_transport_to_all_spots():
        swim_spots = get_swim_spots()
        all_results=[]
        departure_time = int(datetime.datetime.now().timestamp())
        for spot in swim_spots:
            try:
                data = get_transport_data(USER_CITY, spot)
                duration = data["routes"][0]["legs"][0]["duration"]["value"] // 60
                summary = parse_transport_response(data)
                maps_url = generate_maps_link(USER_CITY, spot, departure_time=departure_time)
                all_results.append({
                    "origin": USER_CITY,
                    "destination": spot,
                    "duration_minutes": duration,
                    "route_data": summary,
                    "maps_url": maps_url
            })
            except Exception as e:
                all_results.append({
                    "origin": USER_CITY,
                    "destination": spot,
                    "error": str(e)
            })

        with open("/opt/airflow/dags/src/data/output/transport.json", "w") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

    def task_fetch_podcasts():
        episodes =get_latest_episodes_for_all_podcasts(10)
        with open("/opt/airflow/dags/src/data/output/podcasts.json", "w", encoding="utf-8") as f:
            json.dump(episodes, f, ensure_ascii=False, indent=2)
    
    t1 = PythonOperator(
        task_id="fetch_weather_forecast",
        python_callable=task_fetch_weather_forecast,
        
    )

    t2 = PythonOperator(
        task_id="generate_checklist",
        python_callable=task_generate_checklist,
        
    )

    t3 = PythonOperator(
        task_id="fetch_lake_temperatures",
        python_callable=task_fetch_lake_temperatures,
        
    )

    t4 = PythonOperator(
        task_id="fetch_transport_to_all_spots",
        python_callable=task_fetch_transport_to_all_spots,
    )

    t5 = PythonOperator(
        task_id="fetch_podcasts",
        python_callable=task_fetch_podcasts,
    )

    t1 >> t2 >> t3 >> t4 >> t5
