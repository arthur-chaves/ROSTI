from dotenv import load_dotenv
import psycopg2
import os

# Carrega o .env (arquivo padrão)
load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("HOLIDAY_HOST"),
        port=os.getenv("HOLIDAY_PORT"),
        dbname=os.getenv("HOLIDAY_DB"),
        user=os.getenv("HOLIDAY_USER"),
        password=os.getenv("HOLIDAY_PASSWORD"),
    )

def insert_mood(mood: str):
    con = get_connection()
    with con:
        with con.cursor() as cur:
            cur.execute("INSERT INTO mood_log (mood) VALUES (%s)", (mood,))
    con.close()

def get_latest_mood():
    con = get_connection()
    with con:
        with con.cursor() as cur:
            cur.execute("SELECT mood FROM mood_log ORDER BY timestamp DESC LIMIT 1")
            result = cur.fetchone()
    con.close()
    return result[0] if result else None


def create_weather_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_raw (
            id SERIAL PRIMARY KEY,
            temperature_celsius REAL,
            condition TEXT,
            timestamp TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tabela 'weather_raw' criada com sucesso.")