def get_recommendations_by_mood(mood: str) -> dict:
    if mood == "Relaxado":
        return {
            "filme": "Forrest Gump",
            "passeio": "Passeio leve no Lac Leman"
        }
    elif mood == "Aventureiro":
        return {
            "filme": "127 Horas",
            "passeio": "Trilha no Monte Rigi"
        }
    elif mood == "Caseiro":
        return {
            "filme": "Interstellar",
            "passeio": "Ficar em casa com chocolate quente ☕"
        }
    return {}
