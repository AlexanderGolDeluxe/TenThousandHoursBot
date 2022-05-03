import os
import sqlite3
from typing import List

conn = sqlite3.connect(os.path.join("db/ten_thousand_hours.db"))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


def insert(table: str, column_values: dict):
    columns = ', '.join( column_values.keys() )
    values = [tuple(column_values.values())]
    placeholders = ", ".join( "?" * len(column_values.keys()) )
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def update(table: str, column_values: dict, where_params: dict):
    filled_columns = ', '.join(
        f"{column} = ?" for column in column_values.keys()
    )
    values = [tuple(column_values.values())]
    where_command = create_where_command(where_params)
    cursor.executemany(
        f"UPDATE {table} SET {filled_columns} {where_command}",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str] = ["*"],
    where_params: dict = {}) -> sqlite3.Row:

    columns_joined = ", ".join(columns)
    if where_params:
        where_command = create_where_command(where_params)
        cursor.execute(
            f"SELECT {columns_joined} "
            f"FROM {table} "
            f"{where_command}"
        )
    else:
        cursor.execute(f"SELECT {columns_joined} FROM {table}")
    
    return cursor.fetchall()


def delete(table: str, where_params: dict) -> None:
    where_command = create_where_command(where_params)
    cursor.execute(f"DELETE FROM {table} {where_command}")
    conn.commit()


def get_cursor():
    return cursor


def create_where_command(where_params: dict, params_sep: str = " AND "):
    """Возвращает команду WHERE с указанными параметрами"""
    where_command = params_sep.join(
        f"{column} = '{value}'" for column, value in where_params.items()
    )
    return "WHERE " + where_command


def _init_db():
    """Инициализирует БД"""
    with open("db/createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name='users'"
    )
    table_exists = cursor.fetchall()
    if not table_exists:
        _init_db()

check_db_exists()
