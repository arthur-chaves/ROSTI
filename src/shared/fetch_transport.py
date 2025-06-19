import requests
from dotenv import load_dotenv
import sys
import os
import time
import json
from datetime import datetime, timedelta
from app.utils.db_utils import get_connection

# Carregar variáveis de ambiente
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")


def get_transport_data(origin: str, destination: str, departure_time="now"):
    """
    Consulta o trajeto detalhado de transporte público entre origem e destino,
    com fallback caso o modo ônibus (bus) não encontre resultados.

    Args:
        origin (str): endereço ou coordenadas "lat,lng" da origem
        destination (str): endereço ou coordenadas "lat,lng" do destino
        departure_time (str ou int): 'now' ou timestamp unix da hora de saída

    Returns:
        dict: Dados da resposta da Directions API
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"

    if departure_time == "now":
        # Substitui 'now' por timestamp real para maior controle
        departure_time = int(time.time())

    modes_to_try = ["bus", None]  # tenta com 'bus', depois com todos os transportes
    for transit_mode in modes_to_try:
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "transit",
            "departure_time": departure_time,
            "key": API_KEY,
            "language": "pt-BR",
            "alternatives": "true"
        }
        if transit_mode:
            params["transit_mode"] = transit_mode

        response = requests.get(url, params=params)
        print(f"[DEBUG] Params usados: {params}")
        data = response.json()
        print("[DEBUG] Resposta da API:", data)

        if response.status_code != 200:
            raise Exception(f"Erro na requisição HTTP: {response.status_code}")

        if data.get("status") == "OK":
            return data
        else:
            print(f"[AVISO] Tentativa com transit_mode={transit_mode} falhou: {data.get('status')}")

    raise Exception("Nenhuma rota válida encontrada pela Directions API.")


def parse_transport_response(data):
    """
    Extrai informações detalhadas do trajeto de ônibus (linha, parada e horário).

    Args:
        data (dict): JSON retornado pela Directions API

    Returns:
        str: mensagem formatada com as informações da viagem ou erro
    """
    try:
        routes = data.get("routes", [])
        if not routes:
            return "Nenhuma rota encontrada."

        steps = routes[0].get("legs", [])[0].get("steps", [])
        if not steps:
            return "Nenhuma etapa encontrada no trajeto."

        for step in steps:
            if step.get("travel_mode") == "TRANSIT":
                details = step.get("transit_details", {})
                line = details.get("line", {}).get("short_name", "N/D")
                departure_stop = details.get("departure_stop", {}).get("name", "N/D")
                departure_time = details.get("departure_time", {}).get("text", "N/D")
                arrival_stop = details.get("arrival_stop", {}).get("name", "N/D")
                arrival_time = details.get("arrival_time", {}).get("text", "N/D")
                duration = routes[0]["legs"][0].get("duration", {}).get("text", "N/D")
                distance = routes[0]["legs"][0].get("distance", {}).get("text", "N/D")

                return (
                    f"Pegue o ônibus {line} na parada '{departure_stop}' às {departure_time}.\n"
                    f"Você vai chegar na parada '{arrival_stop}' às {arrival_time}.\n"
                    f"Duração total: {duration} ({distance})."
                )

        return "Não foi possível encontrar uma etapa de ônibus no trajeto."
    except Exception as e:
        return f"Erro ao processar os dados de trânsito: {e}"


def insert_transport(origin, destination, duration_minutes):
    """
    Insere os dados de transporte no banco de dados.

    Args:
        origin (str)
        destination (str)
        duration_minutes (int)
    """
    con = get_connection()
    try:
        with con:
            with con.cursor() as cur:
                cur.execute("""
                    INSERT INTO transport_raw (origin, destination, duration_minutes)
                    VALUES (%s, %s, %s)
                """, (origin, destination, duration_minutes))
    finally:
        con.close()


def load_mock_response(file_path="mock_transport.json"):
    """
    Carrega um mock de resposta da API para testes locais/offline.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    ORIGIN = "Lausanne, Switzerland"
    DESTINATION = "Plage de Vidy-Bourget, Switzerland"

    # Você pode trocar para True para testar com mock local
    USE_MOCK = False

    if USE_MOCK:
        data = load_mock_response()
    else:
        # Exemplo de horário fixo: terça-feira às 9h
        next_tuesday = datetime.now() + timedelta((1 - datetime.now().weekday()) % 7)
        fixed_time = datetime.combine(next_tuesday, datetime.strptime("09:00", "%H:%M").time())
        departure_timestamp = int(fixed_time.timestamp())

        data = get_transport_data(ORIGIN, DESTINATION, departure_time=departure_timestamp)

    message = parse_transport_response(data)
    print(message)


def simplify_directions_response(data):
    if data.get("status") != "OK":
        return {"status": data.get("status"), "error_message": data.get("error_message")}

    simplified_routes = []
    for route in data.get("routes", []):
        simplified_legs = []
        for leg in route.get("legs", []):
            simplified_steps = []
            for step in leg.get("steps", []):
                step_info = {
                    "travel_mode": step.get("travel_mode"),
                    "instruction": step.get("html_instructions"),
                    "duration": step.get("duration", {}).get("text"),
                    "distance": step.get("distance", {}).get("text"),
                }
                if step.get("travel_mode") == "TRANSIT":
                    transit = step.get("transit_details", {})
                    step_info["transit"] = {
                        "line": transit.get("line", {}).get("short_name"),
                        "vehicle_type": transit.get("line", {}).get("vehicle", {}).get("type"),
                        "departure_stop": transit.get("departure_stop", {}).get("name"),
                        "arrival_stop": transit.get("arrival_stop", {}).get("name"),
                        "departure_time": transit.get("departure_time", {}).get("text"),
                        "arrival_time": transit.get("arrival_time", {}).get("text"),
                    }
                simplified_steps.append(step_info)
            simplified_legs.append({
                "start_address": leg.get("start_address"),
                "end_address": leg.get("end_address"),
                "duration": leg.get("duration", {}).get("text"),
                "distance": leg.get("distance", {}).get("text"),
                "steps": simplified_steps,
            })
        simplified_routes.append({
            "summary": route.get("summary"),
            "legs": simplified_legs,
        })
    return {
        "status": data.get("status"),
        "routes": simplified_routes,
    }

def generate_transport_summary(data):
    """
    Gera uma mensagem simples com a informação essencial do trajeto, só ônibus + caminhada + destino.
    """
    try:
        leg = data["routes"][0]["legs"][0]
        steps = leg["steps"]

        bus_line = None
        departure_stop = None
        departure_time = None
        walking_duration = 0

        for step in steps:
            if step["travel_mode"] == "TRANSIT":
                transit = step["transit_details"]
                bus_line = transit["line"]["short_name"]
                departure_stop = transit["departure_stop"]["name"]
                departure_time = transit["departure_time"]["text"]
            elif step["travel_mode"] == "WALKING":
                walking_duration += step["duration"]["value"]  # segundos

        walking_minutes = walking_duration // 60
        destination = leg.get("end_address", "seu destino")

        if bus_line and departure_stop and departure_time:
            return (
                f"Pegue o ônibus {bus_line} na parada '{departure_stop}' às {departure_time}.\n"
                f"Depois, caminhe cerca de {walking_minutes} minutos até {destination}."
            )
        else:
            return "Não foi possível identificar uma rota de ônibus no trajeto."

    except Exception as e:
        return f"Erro ao gerar resumo do trajeto: {e}"

