from contextlib import contextmanager
from typing import Any, Generator
import pyodbc

from backend.core.config import db_settings


def get_db_connection() -> pyodbc.Connection:
    """Abre y retorna una conexión directa pyodbc a SQL Server."""
    try:
        return pyodbc.connect(db_settings.connection_string)
    except Exception as primary_error:
        # Fallback transparente para instancias nombradas locales como .\SQL2025
        if db_settings.server in (".", "localhost", "127.0.0.1"):
            alt_conn = db_settings.connection_string.replace(
                f"SERVER={db_settings.server};", r"SERVER=.\SQL2025;"
            )
            try:
                return pyodbc.connect(alt_conn)
            except Exception:
                pass
        raise primary_error


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
