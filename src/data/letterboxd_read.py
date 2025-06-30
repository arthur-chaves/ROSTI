from app.utils.db_utils import get_connection  # importa do seu módulo
import psycopg2
import csv
import datetime


def get_daily_recommendations(limit=4):
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, year, uri
                FROM letterboxd_watchlist
                WHERE watched = FALSE
                ORDER BY RANDOM()
                LIMIT %s;
            """, (limit,))
            return cur.fetchall()

def mark_as_watched(movie_name: str):
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE letterboxd_watchlist
                SET watched = TRUE, date_watched = %s
                WHERE name = %s AND watched = FALSE;
            """, (datetime.date.today(), movie_name))

def get_all_unwatched():
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name FROM letterboxd_watchlist
                WHERE watched = FALSE
                ORDER BY name;
            """)
            return [row[0] for row in cur.fetchall()]