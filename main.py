import argparse
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = Path(__file__).with_name("car_dealership.db")


QUERIES = {
    "available_trucks": {
        "title": "Покупатели, которым подходит грузовой автомобиль до 2 млн и не старше 2020 г.",
        "sql": """
            SELECT DISTINCT
                p.ID_покупателя AS id_покупателя,
                p.ФИО AS покупатель,
                p.бюджет,
                a.ID_авто AS id_авто,
                a.марка,
                a.год_выпуска,
                a.стоимость,
                p.бюджет - a.стоимость AS остаток_бюджета
            FROM Покупатель AS p
            JOIN Авто AS a
                ON p.бюджет >= a.стоимость
            JOIN Марки AS m
                ON a.марка = m.марка
            WHERE m.категория = 'грузовая'
                AND a.год_выпуска >= 2020
                AND a.стоимость <= 2000000
            ORDER BY p.бюджет DESC, a.стоимость DESC;
        """,
    },
    "birth_year_matches_car_year": {
        "title": "Сколько продаж было покупателям, чей год рождения совпадает с годом выпуска авто",
        "sql": """
            SELECT
                COUNT(*) AS количество_продаж,
                COUNT(DISTINCT p.ID_покупателя) AS количество_покупателей
            FROM Покупатель AS p
            JOIN Продажи AS s
                ON p.ID_покупателя = s.ID_покупателя
            JOIN Авто AS a
                ON s.ID_авто = a.ID_авто
            WHERE strftime('%Y', p.дата_рождения) = CAST(a.год_выпуска AS TEXT);
        """,
    },
    "admin_sales_without_license": {
        "title": "Продажи администраторов покупателям без водительских прав",
        "sql": """
            SELECT
                seller.ID_продавца AS id_продавца,
                seller.ФИО AS продавец,
                COUNT(*) AS количество_продаж,
                SUM(s.стоимость) AS выручка
            FROM Продажи AS s
            JOIN Продавец AS seller
                ON s.ID_продавца = seller.ID_продавца
            JOIN Покупатель AS p
                ON s.ID_покупателя = p.ID_покупателя
            WHERE seller.должность = 'администратор'
                AND p.наличие_прав = 'нету'
            GROUP BY seller.ID_продавца, seller.ФИО
            ORDER BY количество_продаж DESC, выручка DESC;
        """,
    },
    "revenue_by_brand": {
        "title": "Выручка и количество продаж по маркам автомобилей",
        "sql": """
            SELECT
                m.категория,
                a.марка,
                COUNT(*) AS количество_продаж,
                SUM(s.стоимость) AS выручка,
                ROUND(AVG(s.стоимость), 2) AS средняя_цена_продажи
            FROM Продажи AS s
            JOIN Авто AS a
                ON s.ID_авто = a.ID_авто
            JOIN Марки AS m
                ON a.марка = m.марка
            GROUP BY m.категория, a.марка
            ORDER BY выручка DESC;
        """,
    },
    "top_sellers": {
        "title": "Рейтинг продавцов по количеству продаж и выручке",
        "sql": """
            SELECT
                seller.ID_продавца AS id_продавца,
                seller.ФИО AS продавец,
                seller.должность,
                COUNT(*) AS количество_продаж,
                SUM(s.стоимость) AS выручка
            FROM Продажи AS s
            JOIN Продавец AS seller
                ON s.ID_продавца = seller.ID_продавца
            GROUP BY seller.ID_продавца, seller.ФИО, seller.должность
            ORDER BY выручка DESC, количество_продаж DESC;
        """,
    },
    "data_quality_checks": {
        "title": "Базовые проверки качества данных: нет ли продаж без связанных записей",
        "sql": """
            SELECT
                SUM(CASE WHEN a.ID_авто IS NULL THEN 1 ELSE 0 END) AS продажи_без_авто,
                SUM(CASE WHEN seller.ID_продавца IS NULL THEN 1 ELSE 0 END) AS продажи_без_продавца,
                SUM(CASE WHEN p.ID_покупателя IS NULL THEN 1 ELSE 0 END) AS продажи_без_покупателя
            FROM Продажи AS s
            LEFT JOIN Авто AS a
                ON s.ID_авто = a.ID_авто
            LEFT JOIN Продавец AS seller
                ON s.ID_продавца = seller.ID_продавца
            LEFT JOIN Покупатель AS p
                ON s.ID_покупателя = p.ID_покупателя;
        """,
    },
}


def fetch_query(conn: sqlite3.Connection, sql: str):
    cursor = conn.execute(sql)
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    return columns, rows


def print_table(columns, rows, max_rows=None):
    """Мини-вывод таблицы без внешних библиотек."""
    rows_to_print = rows[:max_rows] if max_rows else rows

    if not rows_to_print:
        print("Нет данных")
        return

    table = [columns] + [[str(value) for value in row] for row in rows_to_print]
    widths = [max(len(str(row[i])) for row in table) for i in range(len(columns))]

    def format_row(row):
        return " | ".join(str(value).ljust(widths[i]) for i, value in enumerate(row))

    print(format_row(columns))
    print("-+-".join("-" * width for width in widths))
    for row in rows_to_print:
        print(format_row(row))

    if max_rows and len(rows) > max_rows:
        print(f"... показано {max_rows} из {len(rows)} строк")


def execute_query(db_path: Path, query_name: str, max_rows: int | None = 20):
    query = QUERIES[query_name]
    print(f"\n{query['title']}\n")

    with sqlite3.connect(db_path) as conn:
        columns, rows = fetch_query(conn, query["sql"])

    print_table(columns, rows, max_rows=max_rows)


def execute_all_queries(db_path: Path, max_rows: int | None = 20):
    for query_name in QUERIES:
        execute_query(db_path, query_name, max_rows=max_rows)


def parse_args():
    parser = argparse.ArgumentParser(description="Небольшой анализ данных автосалона в SQLite")
    parser.add_argument(
        "--db",
        default=DEFAULT_DB_PATH,
        type=Path,
        help="Путь к SQLite-базе. По умолчанию используется car_dealership.db рядом со скриптом.",
    )
    parser.add_argument(
        "--query",
        choices=["all", *QUERIES.keys()],
        default="all",
        help="Какой запрос выполнить. По умолчанию запускаются все запросы.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=20,
        help="Сколько строк показывать для каждого запроса. 0 — показать все строки.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    max_rows = None if args.max_rows == 0 else args.max_rows

    if not args.db.exists():
        raise FileNotFoundError(f"База данных не найдена: {args.db}")

    if args.query == "all":
        execute_all_queries(args.db, max_rows=max_rows)
    else:
        execute_query(args.db, args.query, max_rows=max_rows)


if __name__ == "__main__":
    main()
