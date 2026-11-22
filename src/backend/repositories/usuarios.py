from typing import NamedTuple
from backend.db.connection import get_db_cursor


class UsuarioRecord(NamedTuple):
    id_usuario: int
    email: str
    password: str


class UsuarioRepository:
    """Acceso a datos de la tabla Usuario (idUsuario, email, password) en SQL Server."""

    def get_by_email(self, email: str) -> UsuarioRecord | None:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT idUsuario, email, password FROM Usuario WHERE email = ?",
                (email,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return UsuarioRecord(
                id_usuario=int(row[0]),
                email=str(row[1]),
                password=str(row[2]),
            )

    def exists(self, email: str) -> bool:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1 FROM Usuario WHERE email = ?", (email,))
            return cursor.fetchone() is not None

    def create(self, email: str, password_hash: str) -> UsuarioRecord:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO Usuario (email, password)
                OUTPUT INSERTED.idUsuario, INSERTED.email, INSERTED.password
                VALUES (?, ?)
                """,
                (email, password_hash),
            )
            row = cursor.fetchone()
            return UsuarioRecord(
                id_usuario=int(row[0]),
                email=str(row[1]),
                password=str(row[2]),
            )


usuario_repository = UsuarioRepository()
