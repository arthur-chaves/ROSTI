import pandas as pd
from pathlib import Path


# Dados fictícios
data = [
    {"mood": "feliz", "title": "The Secret Life of Walter Mitty", "type": "filme"},
    {"mood": "triste", "title": "The Pursuit of Happyness", "type": "filme"},
    {"mood": "cansado", "title": "Midnight Diner", "type": "série"},
    {"mood": "animado", "title": "Brooklyn Nine-Nine", "type": "série"},
    {"mood": "feliz", "title": "Paddington 2", "type": "filme"},
    {"mood": "triste", "title": "Blue Valentine", "type": "filme"},
]

# Criar DataFrame
df = pd.DataFrame(data)

# Caminho de destino (ex: data/media/mock_media.csv)
output_path = Path(__file__).resolve().parents[1] / "data" / "media"
output_path.mkdir(parents=True, exist_ok=True)

# Salvar CSV
df.to_csv(output_path / "mock_media.csv", index=False)

print("Mock de dados de mídia criado com sucesso!")
