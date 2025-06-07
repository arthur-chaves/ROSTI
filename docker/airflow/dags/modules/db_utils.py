import duckdb

def get_connection():
    return duckdb.connect("src/data/holiday_helper.db")

def insert_mood(mood: str):
    con = get_connection()
    con.execute("INSERT INTO mood_log (mood) VALUES (?)", (mood,))
    con.close()

def get_latest_mood():
    con = get_connection()
    result = con.execute("SELECT mood FROM mood_log ORDER BY timestamp DESC LIMIT 1").fetchone()
    con.close()
    return result[0] if result else None
