
from random import uniform
from .fetch_transport import get_transport_data, parse_transport_response
from .location_utils import get_user_coordinates

def get_mock_water_temperature():
    return round(uniform(19.5, 24.0), 1)  # Temperatura realista de verão

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

        return (
            f"Hoje, a {lake['name']} em {lake['city']} está com {lake['temp']}°C, "
            f"uma ótima temperatura para nadar! "
            f"O tempo estimado de transporte público saindo da sua localização até lá é de "
            f"{duration_minutes} minutos."
        )
    except Exception as e:
        return f"Erro ao buscar tempo de trajeto: {str(e)}"
