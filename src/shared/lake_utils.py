
from random import uniform
from .fetch_transport import get_transport_data, parse_transport_response
from .location_utils import get_user_coordinates
from app.utils.db_utils import get_connection  # importa do seu módulo
import psycopg2

TARGET_HOURS = {"09:00:00", "12:00:00", "15:00:00", "18:00:00"}


def is_pleasant_to_swim(temp_celsius: float) -> bool:
    # Critério baseado no Lago Léman
    return 20.0 <= temp_celsius <= 25.0

def get_mock_water_temperature():
    return round(uniform(18.0, 24.0), 1)  # Temperatura realista de verão

def get_mock_best_lake_today():
    return {
        "name": "Plage de Vidy-Bourget",
        "city": "Lausanne",
        "coords": "46.5165,6.5946",
        "temp": get_mock_water_temperature()
    }


def build_mock_transport_message():
    lake = get_mock_best_lake_today()
    origin_coords = get_user_coordinates()

    try:
        data = get_transport_data(origin_coords, lake["coords"])
        duration_minutes, _ = parse_transport_response(data)

        swim_message = (
            "uma ótima temperatura para nadar!"
            if is_pleasant_to_swim(lake["temp"])
            else "a temperatura da água está um pouco fria para nadar."
        )

        return (
            f"Hoje, a {lake['name']} em {lake['city']} está com {lake['temp']}°C, "
            f"uma ótima temperatura para nadar! "
            f"O tempo estimado de transporte público saindo da sua localização até lá é de "
            f"{duration_minutes} minutos."
        )
    except Exception as e:
        return f"Erro ao buscar tempo de trajeto: {str(e)}"

import requests
from datetime import datetime, timezone, timedelta

def get_lake_temperature_today(lake: str, lat: float, lng: float, depth=1.5):
    now = datetime.now(timezone.utc)
    if now.hour >= 18:
            target_date = now.date() + timedelta(days=1)
    else:
            target_date = now.date()

    start_str = now.strftime("%Y%m%d0000")
    end_str = now.strftime("%Y%m%d2359")

    url = (
        f"https://alplakes-api.eawag.ch/simulations/point/delft3d-flow/"
        f"{lake}/{start_str}/{end_str}/{depth}/{lat}/{lng}"
        "?variables=temperature"
    )

    try:
        resp = requests.get(url, headers={"accept": "application/json"})
        resp.raise_for_status()
        data = resp.json()
        temps = data["variables"]["temperature"]["data"]
        times = data["time"]

        today = now.date()
        filtered_temps = [
            temp for t, temp in zip(times, temps)
            if datetime.fromisoformat(t).date() == today and
               datetime.fromisoformat(t).strftime("%H:%M:%S") in TARGET_HOURS
        ]
        if not filtered_temps:
            return None, "Sem dados nos horários desejados"
        avg = round(sum(filtered_temps) / len(filtered_temps), 1)
        return avg, f"{len(filtered_temps)} medições filtradas"
    except Exception as e:
        return None, str(e)

def get_all_spots():
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name, lake, lat, lng FROM swim_spots;")
            return cur.fetchall()

def process_all_lakes_today():
    spots = get_all_spots()
    for name, lake, lat, lng in spots:
        temp, status = get_lake_temperature_today(lake, lat, lng)
        print(f"{name} ({lake}) → {temp}°C ({status})")
