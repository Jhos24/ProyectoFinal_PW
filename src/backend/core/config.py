import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Localizar y cargar el archivo .env desde la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


@dataclass(frozen=True)
class DatabaseSettings:
    """Configuración de conexión a SQL Server mediante SQL Server Authentication.

    Siguiendo las especificaciones del proyecto, no se incluye ni se configura puerto.
    """

    server: str = os.getenv("DB_SERVER", "localhost")
    database: str = os.getenv("DB_DATABASE", "")
    user: str = os.getenv("DB_USER", "")
    password: str = os.getenv("DB_PASSWORD", "")
    driver: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    trust_server_certificate: str = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")

    @property
    def connection_string(self) -> str:
        """Genera la cadena de conexión ODBC sin especificar puerto."""
        return (
            f"DRIVER={self.driver};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"TrustServerCertificate={self.trust_server_certificate};"
        )


db_settings = DatabaseSettings()
