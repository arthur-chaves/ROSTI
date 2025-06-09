# # Imagem base Python leve
# FROM python:3.10-slim

# # Diretório dentro do container
# WORKDIR /src

# # Instala dependências do sistema necessárias (ex: psycopg2)
# RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# # Copia requirements e instala libs
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# # Copia todo o código para dentro do container
# COPY . .

# # Expõe a porta do Streamlit
# EXPOSE 8501

# # Comando para rodar o Streamlit na porta 8501 escutando em todas interfaces
# CMD ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
