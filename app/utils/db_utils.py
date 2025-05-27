import duckdb

def get_connection():
    return duckdb.connect("data/holiday_helper.db")

def insert_mood(mood: str):
    con = get_connection()
    con.execute("INSERT INTO mood_log (mood) VALUES (?)", (mood,))
    con.close()
