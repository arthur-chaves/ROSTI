import duckdb

def get_connection():
    return duckdb.connect("data/holiday_helper.db")
