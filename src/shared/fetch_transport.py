
import requests
from dotenv import load_dotenv
import sys
import os

# app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")


def get_transport_data(origin: str, destination: str, departure_time="now"):
    """
    Consulta o trajeto detalhado de transporte público (ônibus) entre origem e destino.
    
    Args:
        origin (str): endereço ou coordenadas "lat,lng" da origem
        destination (str): endereço ou coordenadas "lat,lng" do destino
        departure_time (str ou int): 'now' ou timestamp unix da hora de saída
    
    Returns:
        dict: Dados da resposta da Directions API
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": origin,
        "destination": destination,
        "mode": "transit",
        "transit_mode": "bus",
        "departure_time": departure_time,
        "key": API_KEY,
        "language": "pt-BR"
    }

    response = requests.get(url, params=params)
    print("Google Directions API response:", response.json())  # <<<<< Aqui
    if response.status_code != 200:
        raise Exception(f"Erro na requisição HTTP: {response.status_code}")

    data = response.json()
    if data.get("status") != "OK":
        raise Exception(f"Erro na API: {data.get('status')} - {data.get('error_message')}")

    return data


from app.utils.db_utils import get_connection 

def insert_transport(origin, destination, duration_minutes):
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

def parse_transport_response(data):
    """
    Extrai informações detalhadas do trajeto de ônibus (linha, parada e horário).
    
    Args:
        data (dict): JSON retornado pela Directions API
    
    Returns:
        str: mensagem formatada com as informações da viagem ou erro
    """
    try:
        steps = data["routes"][0]["legs"][0]["steps"]
        for step in steps:
            if step["travel_mode"] == "TRANSIT":
                details = step["transit_details"]
                line = details["line"]["short_name"]
                departure_stop = details["departure_stop"]["name"]
                departure_time = details["departure_time"]["text"]
                arrival_stop = details["arrival_stop"]["name"]
                arrival_time = details["arrival_time"]["text"]
                duration = data["routes"][0]["legs"][0]["duration"]["text"]
                distance = data["routes"][0]["legs"][0]["distance"]["text"]

                return (
                    f"Pegue o ônibus {line} na parada '{departure_stop}' às {departure_time}.\n"
                    f"Você vai chegar na parada '{arrival_stop}' às {arrival_time}.\n"
                    f"Duração total: {duration} ({distance})."
                )
        return "Não foi possível encontrar uma etapa de ônibus no trajeto."
    except Exception as e:
        return f"Erro ao processar os dados de trânsito: {e}"




if __name__ == "__main__":
    ORIGIN = "Lausanne, Switzerland"
    DESTINATION = "Plage de Vidy-Bourget, Switzerland"

    data = get_transport_data(ORIGIN, DESTINATION)
    message = parse_transport_response(data)
    print(message)

