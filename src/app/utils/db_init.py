from db_utils import get_connection

def create_tables():
    con = get_connection()
    with con:
        with con.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transport_raw (
                    origin TEXT,
                    destination TEXT,
                    duration_minutes INTEGER,
                    date DATE DEFAULT CURRENT_DATE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mood_log (
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    mood TEXT
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS weather_raw (
                    id SERIAL PRIMARY KEY,
                    temperature_celsius REAL,
                    condition TEXT,
                    timestamp TEXT
                );
            """)
    con.close()

if __name__ == "__main__":
    create_tables()
    print("Tabelas criadas com sucesso.")
