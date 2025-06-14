

def recommend_places(weather_condition):
    """
    Retorna lista de lugares recomendados com base no clima.
    Parâmetro:
      weather_condition (str): descrição simples do clima, ex: "clear", "rain", "clouds"
    Retorna:
      list de dicts com nome e categoria do lugar e link de rota mock
    """
    recommendations = []

    if weather_condition in ["clear", "sunny"]:
        recommendations = [
            {"name": "Parque Nacional Suíço", "category": "Parque", "route_url": "https://maps.google.com/?q=Swiss+National+Park"},
            {"name": "Trilha do Lago Thun", "category": "Trilha", "route_url": "https://maps.google.com/?q=Lago+Thun+Trail"},
            {"name": "Lago de Zurique", "category": "Lago", "route_url": "https://maps.google.com/?q=Lake+Zurich"}
        ]
    elif weather_condition in ["rain", "storm"]:
        recommendations = [
            {"name": "Museu de Arte de Zurique", "category": "Museu", "route_url": "https://maps.google.com/?q=Zurich+Art+Museum"},
            {"name": "Centro Cultural de Genebra", "category": "Centro Cultural", "route_url": "https://maps.google.com/?q=Geneva+Cultural+Center"},
            {"name": "Spa Thermal de Baden", "category": "Spa", "route_url": "https://maps.google.com/?q=Baden+Thermal+Spa"}
        ]
    else:
        recommendations = [
            {"name": "Cidade Velha de Lucerna", "category": "Turismo Histórico", "route_url": "https://maps.google.com/?q=Lucerne+Old+Town"},
            {"name": "Café Charmoso em Berna", "category": "Café", "route_url": "https://maps.google.com/?q=Bern+Cozy+Cafe"}
        ]

    return recommendations
