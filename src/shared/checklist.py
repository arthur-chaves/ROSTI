def generate_checklist(weather_data):
    temp = weather_data.get("temp", 20)
    condition = weather_data.get("weather", "").lower()
    checklist = []
    mensagem = ""

    if "rain" in condition or "storm" in condition:
        checklist = ["guarda-chuva", "jaqueta impermeável", "livro", "power bank"]
        mensagem = "🌧️ Parece que vai chover! Leve algo para se proteger e se entreter."

    elif "clear" in condition and temp >= 25:
        checklist = ["protetor solar", "óculos de sol", "chapéu", "snorkel", "toalha"]
        mensagem = "☀️ Dia perfeito para nadar ou relaxar ao ar livre. Não esqueça o protetor solar!"

    elif "cloud" in condition:
        checklist = ["mochila leve", "tênis confortável", "casaco leve", "livro"]
        mensagem = "⛅ Dia nublado... Ideal para explorar com tranquilidade."

    else:
        checklist = ["mochila", "garrafa de água", "mapa offline"]
        mensagem = "📦 Prepare-se para o inesperado! Um dia neutro pode surpreender."

    return mensagem, checklist
