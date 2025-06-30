from db_utils import get_connection  # importa do seu módulo
import psycopg2
import csv
import datetime
import os

current_dir = os.path.dirname(__file__)  # src/app/utils
csv_path = os.path.abspath(os.path.join(current_dir, "..", "..", "data", "letterboxd_watchlist.csv"))



def import_watchlist(csv_path: str):
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                for row in reader:
                    # Ignora linhas vazias (todas as colunas None ou vazias)
                    if not any(row.values()):
                        continue

                    name = row.get("Name")
                    year_str = row.get("Year")
                    uri = row.get("Letterboxd URI")

                    # Verifica se 'Year' está presente e válido
                    if not year_str or year_str.strip() == "":
                        print(f"Ignorando linha sem ano válido: {row}")
                        continue

                    try:
                        year = int(year_str)
                    except ValueError:
                        print(f"Ano inválido, ignorando linha: {row}")
                        continue

                    # Evita duplicatas pelo par (name, year)
                    cur.execute(
                        "SELECT 1 FROM letterboxd_watchlist WHERE name = %s AND year = %s;",
                        (name, year)
                    )
                    exists = cur.fetchone()
                    if not exists:
                        cur.execute(
                            """
                            INSERT INTO letterboxd_watchlist (name, year, uri)
                            VALUES (%s, %s, %s);
                            """,
                            (name, year, uri)
                        )
if __name__ == "__main__":
    import_watchlist(csv_path)                        