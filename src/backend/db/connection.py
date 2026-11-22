from contextlib import contextmanager
from typing import Any, Generator
import pyodbc

from backend.core.config import db_settings


def get_db_connection() -> pyodbc.Connection:
    """Abre y retorna una conexión directa pyodbc a SQL Server."""
    return pyodbc.connect(db_settings.connection_string)


@contextmanager
def get_db_cursor(commit: bool = False) -> Generator[pyodbc.Cursor, None, None]:
    """Context manager para ejecutar operaciones con pyodbc sin ORM.

    Garantiza el cierre adecuado del cursor y de la conexión, y realiza commit
    o rollback automáticamente si se solicita.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def check_connection() -> dict[str, Any]:
    """Verifica la conectividad con SQL Server ejecutando una consulta simple."""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT @@VERSION AS version, DB_NAME() AS current_db")
        row = cursor.fetchone()
        return {
            "status": "connected",
            "database": row.current_db if row else None,
            "version": row.version if row else None,
        }
