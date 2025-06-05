import pandas as pd
import random
from pathlib import Path



# def get_recommendations_by_mood(mood: str) -> dict:
#     if mood == "Relaxado":
#         return {
#             "filme": "Forrest Gump",
#             "passeio": "Passeio leve no Lac Leman"
#         }
#     elif mood == "Aventureiro":
#         return {
#             "filme": "127 Horas",
#             "passeio": "Trilha no Monte Rigi"
#         }
#     elif mood == "Caseiro":
#         return {
#             "filme": "Interstellar",
#             "passeio": "Ficar em casa com chocolate quente ☕"
#         }
#     return {}


def get_media_by_mood(mood: str) -> dict:
    csv_path = Path(__file__).resolve().parents[2] / "data" / "media" / "mock_media.csv"
    df =pd.read_csv(csv_path)
    filtered = df[df["mood"] == mood]
    if filtered.empty:
        return {"title": "Nenhuma sugestão encontrada", "type": "N/A"}
    choice = filtered.sample(1).iloc[0]
    return {"title": choice["title"], "type": choice["type"]}
