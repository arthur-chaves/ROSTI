
import requests
from dotenv import load_dotenv
import sys
import os

app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

def get_transport_data(origin: str, destination: str, mode="transit"):
    """
    Consulta o tempo de transporte público (bus, metro, etc) entre origem e destino.
    
    Args:
        origin (str): endereço ou coordenadas "lat,lng" da origem (pode ser ponto genérico para preservar privacidade)
        destination (str): endereço ou coordenadas "lat,lng" do destino
        mode (str): modo de transporte, padrão "transit" (transporte público)
        
    Returns:
        dict: Dados da resposta da API
    """
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    params = {
        "origins": origin,
        "destinations": destination,
        "mode": mode,
        "key": API_KEY,
        "language": "pt-BR",
        "transit_mode": "bus",
        "departure_time": "now"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Erro na requisição HTTP: {response.status_code}")

    data = response.json()

    if data.get("status") != "OK":
        raise Exception(f"Erro na API: {data.get('status')} - {data.get('error_message')}")

    return data


def parse_transport_response(data):
    """
    Extrai a duração da viagem em transporte público (ônibus) da resposta da Distance Matrix API
    e retorna uma mensagem amigável.

    Args:
        data (dict): JSON retornado pela API

    Returns:
        str: mensagem formatada com o tempo estimado ou mensagem de erro
    """
    try:
        element = data["rows"][0]["elements"][0]
        status = element.get("status", "")

        if status != "OK":
            return f"Não foi possível obter a rota: {status}"

        duration = element["duration"]["text"]  # ex: "45 mins"
        distance = element["distance"]["text"]  # ex: "10 km"

        return f"O tempo estimado de ônibus de Lausanne até o Lago de Genebra é de {duration} ({distance})."

    except (IndexError, KeyError):
        return "Resposta da API está em formato inesperado."

if __name__ == "__main__":
    # Usando coordenadas genéricas ou nome da cidade para anonimizar
    ORIGIN = "Lausanne, Switzerland"  # Ou algo como "46.5191,6.6336" (lat,lng)
    DESTINATION = "Lac Léman, Switzerland"  # Lake Geneva em francês

    data = get_transport_data(ORIGIN, DESTINATION)
    message = parse_transport_response(data)
    print(data)

from utils.db_utils import get_connection # type: ignore

def insert_transport(origin, destination, duration_minutes):
    con = get_connection()
    con.execute("""
        INSERT INTO transport_raw (origin, destination, duration_minutes)
        VALUES (?, ?, ?)
    """, (origin, destination, duration_minutes))
    con.close()
