"""SQLite data-access helpers."""

from __future__ import annotations


import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DEFAULT_DB_PATH = BASE_DIR / "calculator.db"

DB_PATH = Path(
    os.getenv(
        "DATABASE_PATH",
        str(DEFAULT_DB_PATH),
    )
)


def get_connection():
    """创建数据库连接。"""

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def init_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS calculation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
            """
        )
        connection.commit()


def save_history(expression: str, result: int | float) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO calculation_history (expression, result)
            VALUES (?, ?)
            """,
            (expression, str(result)),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_history(limit: int = 100) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, expression, result, created_at
            FROM calculation_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def delete_history(history_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM calculation_history WHERE id = ?",
            (history_id,),
        )
        connection.commit()
        return cursor.rowcount > 0


def clear_history() -> int:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM calculation_history")
        connection.commit()
        return cursor.rowcount
