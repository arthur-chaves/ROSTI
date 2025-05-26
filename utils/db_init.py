from db_utils import get_connection

def create_tables():
    con = get_connection()
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS transport_raw (
            origin TEXT,
            destination TEXT,
            duration_minutes INTEGER,
            date DATE DEFAULT CURRENT_DATE
        );
    """)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS mood_log (
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            mood TEXT
        );
    """)
    
    con.close()

if __name__ == "__main__":
    create_tables()
    print("Tabelas criadas com sucesso.")
