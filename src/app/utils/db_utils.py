import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        host="postgres",
        port=5432,
        user="airflow",
        password="airflow",
        dbname="airflow"
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

