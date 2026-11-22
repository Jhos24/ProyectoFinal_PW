import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

from backend.core.config import DatabaseSettings
from backend.repositories.personas import PersonaRepository
from backend.schemas.personas import Persona, PersonaCreate, PersonaUpdate


class TestDatabaseConfig(TestCase):
    def test_connection_string_does_not_contain_port(self):
        settings = DatabaseSettings(
            server="127.0.0.1",
            database="test_db",
            user="test_user",
            password="secret_password",
            driver="ODBC Driver 17 for SQL Server",
        )
        conn_str = settings.connection_string

        # Verificar que contiene los parámetros requeridos
        self.assertIn("DRIVER=ODBC Driver 17 for SQL Server", conn_str)
        self.assertIn("SERVER=127.0.0.1", conn_str)
        self.assertIn("DATABASE=test_db", conn_str)
        self.assertIn("UID=test_user", conn_str)
        self.assertIn("PWD=secret_password", conn_str)

        # Verificar estrictamente que no existe configuración de puerto
        self.assertNotIn("PORT", conn_str)
        self.assertNotIn(":1433", conn_str)
        self.assertNotIn(",1433", conn_str)


class TestPersonaRepository(TestCase):
    def setUp(self):
        self.repo = PersonaRepository()

    @patch("backend.repositories.personas.get_db_cursor")
    def test_list_personas(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        # Simula filas devueltas por pyodbc
        mock_cursor.fetchall.return_value = [
            ("12345678", "Juan Perez", datetime.date(1995, 5, 20)),
            ("87654321", "Maria Lopez", datetime.date(1992, 10, 15)),
        ]

        result = self.repo.list()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].dni, "12345678")
        self.assertEqual(result[0].nombre, "Juan Perez")
        self.assertEqual(result[0].fecha_nacimiento, datetime.date(1995, 5, 20))
        mock_cursor.execute.assert_called_once_with(
            "SELECT dni, nombre, fechaNacimiento FROM Persona"
        )

    @patch("backend.repositories.personas.get_db_cursor")
    def test_get_persona_found(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (
            "12345678",
            "Carlos Diaz",
            datetime.date(1998, 1, 1),
        )

        persona = self.repo.get("12345678")

        self.assertIsNotNone(persona)
        self.assertEqual(persona.dni, "12345678")
        self.assertEqual(persona.nombre, "Carlos Diaz")
        mock_cursor.execute.assert_called_once_with(
            "SELECT dni, nombre, fechaNacimiento FROM Persona WHERE dni = ?",
            ("12345678",),
        )

    @patch("backend.repositories.personas.get_db_cursor")
    def test_get_persona_not_found(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        persona = self.repo.get("99999999")

        self.assertIsNone(persona)

    @patch("backend.repositories.personas.get_db_cursor")
    def test_add_persona(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        nueva = Persona(
            dni="11223344",
            nombre="Laura Ruiz",
            fecha_nacimiento=datetime.date(2000, 3, 25),
        )

        creada = self.repo.add(nueva)

        self.assertEqual(creada.dni, "11223344")
        mock_get_cursor.assert_called_once_with(commit=True)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO Persona (dni, nombre, fechaNacimiento) VALUES (?, ?, ?)",
            ("11223344", "Laura Ruiz", datetime.date(2000, 3, 25)),
        )

    @patch.object(PersonaRepository, "exists", return_value=True)
    @patch("backend.repositories.personas.get_db_cursor")
    def test_update_persona(self, mock_get_cursor, mock_exists):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        datos = PersonaUpdate(
            nombre="Laura Modificada",
            fecha_nacimiento=datetime.date(2000, 3, 25),
        )

        actualizada = self.repo.update("11223344", datos)

        self.assertIsNotNone(actualizada)
        self.assertEqual(actualizada.nombre, "Laura Modificada")
        mock_cursor.execute.assert_called_once_with(
            "UPDATE Persona SET nombre = ?, fechaNacimiento = ? WHERE dni = ?",
            ("Laura Modificada", datetime.date(2000, 3, 25), "11223344"),
        )

    @patch("backend.repositories.personas.get_db_cursor")
    def test_delete_persona(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        deleted = self.repo.delete("11223344")

        self.assertTrue(deleted)
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM Persona WHERE dni = ?", ("11223344",)
        )


class TestConnectionModule(TestCase):
    @patch("backend.db.connection.get_db_connection")
    def test_get_db_cursor_commit_on_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        from backend.db.connection import get_db_cursor

        with get_db_cursor(commit=True) as cursor:
            cursor.execute("SELECT 1")

        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("backend.db.connection.get_db_connection")
    def test_get_db_cursor_rollback_on_exception(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        from backend.db.connection import get_db_cursor

        with self.assertRaises(RuntimeError):
            with get_db_cursor(commit=True) as cursor:
                raise RuntimeError("Database error simulated")

        mock_conn.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("backend.db.connection.get_db_cursor")
    def test_check_connection_success(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_row = MagicMock()
        mock_row.version = "Microsoft SQL Server 2022"
        mock_row.current_db = "personas_db"
        mock_cursor.fetchone.return_value = mock_row

        from backend.db.connection import check_connection

        info = check_connection()
        self.assertEqual(info["status"], "connected")
        self.assertEqual(info["database"], "personas_db")
        self.assertEqual(info["version"], "Microsoft SQL Server 2022")

