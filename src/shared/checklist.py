def generate_checklist(forecast_data):
    max_temp = forecast_data.get("max_temp", 22)
    min_temp = forecast_data.get("min_temp", 16)
    day_desc = forecast_data.get("day_desc", "").lower()
    night_desc = forecast_data.get("night_desc", "").lower()

    checklist = []
    mensagem = ""

    # Condição de chuva ou tempestade
    if "rain" in day_desc or "storm" in day_desc:
        checklist = ["guarda-chuva", "jaqueta impermeável", "livro", "power bank", "meias extras"]
        mensagem = "🌧️ Parece que vai chover! Leve algo para se proteger e se entreter."

    # Condição de sol forte e calor
    elif "clear" in day_desc and max_temp >= 25:
        checklist = ["protetor solar", "óculos de sol", "chapéu", "snorkel", "toalha", "garrafa d'água", "power bank", "shopping bag"]
        mensagem = "☀️ Dia perfeito para nadar ou relaxar ao ar livre. Não esqueça o protetor solar!"

    # Condição de tempo nublado
    elif "cloud" in day_desc:
        checklist = ["mochila leve", "tênis confortável", "casaco leve", "livro", "garrafa d'água"]
        mensagem = "⛅ Dia nublado... Ideal para explorar com tranquilidade."

    else:
        checklist = ["mochila", "garrafa de água", "mapa offline", "snacks"]
        mensagem = "📦 Prepare-se para o inesperado! Um dia neutro pode surpreender."

    # Adicionais se a noite for fria
    if min_temp < 15:
        checklist.append("agasalho extra")

    # Remove duplicatas se houver
    checklist = sorted(set(checklist))

    return mensagem, checklist
