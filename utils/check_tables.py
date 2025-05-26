from db_utils import get_connection

def list_tables():
    con = get_connection()
    result = con.execute("SHOW TABLES").fetchall()
    con.close()
    return result

if __name__ == "__main__":
    tables = list_tables()
    print("Tabelas existentes no banco:")
    for table in tables:
        print(table[0])
