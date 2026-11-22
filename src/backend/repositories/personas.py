from backend.db.connection import get_db_cursor
from backend.schemas.personas import Persona, PersonaUpdate


class PersonaRepository:
    """Acceso a datos de personas en Microsoft SQL Server mediante pyodbc sin ORM."""

    def list(self) -> list[Persona]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT dni, nombre, fechaNacimiento FROM Persona")
            rows = cursor.fetchall()
            return [
                Persona(
                    dni=str(row[0]),
                    nombre=str(row[1]),
                    fecha_nacimiento=row[2],
                )
                for row in rows
            ]

    def get(self, dni: str) -> Persona | None:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT dni, nombre, fechaNacimiento FROM Persona WHERE dni = ?",
                (dni,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Persona(
                dni=str(row[0]),
                nombre=str(row[1]),
                fecha_nacimiento=row[2],
            )

    def exists(self, dni: str) -> bool:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1 FROM Persona WHERE dni = ?", (dni,))
            return cursor.fetchone() is not None

    def add(self, persona: Persona) -> Persona:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "INSERT INTO Persona (dni, nombre, fechaNacimiento) VALUES (?, ?, ?)",
                (persona.dni, persona.nombre, persona.fecha_nacimiento),
            )
        return persona

    def update(self, dni: str, datos: PersonaUpdate) -> Persona | None:
        if not self.exists(dni):
            return None

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE Persona SET nombre = ?, fechaNacimiento = ? WHERE dni = ?",
                (datos.nombre, datos.fecha_nacimiento, dni),
            )
        return Persona(dni=dni, **datos.model_dump())

    def delete(self, dni: str) -> bool:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM Persona WHERE dni = ?", (dni,))
            return cursor.rowcount > 0


persona_repository = PersonaRepository()
