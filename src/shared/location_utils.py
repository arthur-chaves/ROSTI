
import os
from dotenv import load_dotenv

load_dotenv()

def get_user_coordinates():
    lat = os.getenv("user_lat")
    lng = os.getenv("user_lng")
    if not lat or not lng:
        raise ValueError("Coordenadas do usuário não definidas no .env")
    return f"{lat},{lng}"
