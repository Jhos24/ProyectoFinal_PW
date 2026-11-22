"""Script de utilidad para comprobar la conexión a SQL Server y verificar la tabla Persona."""

import sys
from backend.core.config import db_settings
from backend.db.connection import check_connection, get_db_cursor


def main() -> None:
    print("=" * 60)
    print(" Verificando conexión a SQL Server...")
    print(f" Servidor:  {db_settings.server}")
    print(f" Base datos:{db_settings.database}")
    print(f" Usuario:   {db_settings.user}")
    print(f" Driver:    {db_settings.driver}")
    print(" (Nota: No se utiliza puerto en la configuración)")
    print("=" * 60)

    try:
        info = check_connection()
        print("\n ¡Conexión exitosa a SQL Server!")
        print(f" Base de datos activa: {info.get('database')}")
        print(f" Versión del servidor: {info.get('version')}")

        # Comprobar la existencia y conteo de la tabla Persona
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM Persona")
            total = cursor.fetchone()[0]
            print(f" Registros actuales en tabla 'Persona': {total}")

    except Exception as e:
        print(f"\n Error al conectar o consultar SQL Server:\n {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
