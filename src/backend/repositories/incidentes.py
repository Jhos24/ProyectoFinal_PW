from datetime import datetime, timezone, timedelta
import logging
import time
from backend.db.connection import get_db_cursor
from backend.schemas.incidentes import (
    IncidenteCreate,
    IncidenteOut,
    IncidenteUpdate,
    EstadoIncidente,
    GravedadIncidente,
    TipoResiduo,
)

logger = logging.getLogger(__name__)


class IncidenteRepository:
    """Acceso a datos de incidentes ambientales en Microsoft SQL Server con pyodbc sin ORM."""

    def __init__(self) -> None:
        self._table_initialized = False
        self._db_available: bool | None = None
        self._last_db_check: float = 0
        self._memory_cache: list[IncidenteOut] = []
        self._seed_initial_data()

    def _seed_initial_data(self) -> None:
        """Carga datos de demostración realistas de Huancayo si se requiere."""
        base_time = datetime.now() - timedelta(days=2)
        demo_items = [
            IncidenteOut(
                id=1,
                codigo_alerta="ECO-HYO-1001",
                latitud=-12.0678,
                longitud=-75.2091,
                direccion_referencia="Av. Ferrocarril c/ Jr. Puno",
                distrito="Huancayo Centro",
                tipo_residuo=TipoResiduo.PLASTICOS,
                gravedad=GravedadIncidente.MEDIA,
                detalles="Acumulación de envases plásticos y bolsas que obstruyen la cuneta pluvial tras día de feria.",
                evidencia_url="https://images.unsplash.com/photo-1530587191325-3db32d826c18?auto=format&fit=crop&w=600&q=80",
                estado=EstadoIncidente.PENDIENTE,
                fecha_registro=base_time + timedelta(hours=3),
                fecha_atencion=None,
                observaciones_fiscalizacion=None,
                tiempo_respuesta_horas=None,
            ),
            IncidenteOut(
                id=2,
                codigo_alerta="ECO-HYO-1002",
                latitud=-12.0543,
                longitud=-75.2165,
                direccion_referencia="Riberas del Río Shullcas, altura Jr. Tarapacá",
                distrito="El Tambo",
                tipo_residuo=TipoResiduo.PELIGROSOS,
                gravedad=GravedadIncidente.CRITICA,
                detalles="Vertido clandestino de jeringas, apósitos y restos hospitalarios en el talud del río.",
                evidencia_url="https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?auto=format&fit=crop&w=600&q=80",
                estado=EstadoIncidente.PENDIENTE,
                fecha_registro=base_time + timedelta(hours=8),
                fecha_atencion=None,
                observaciones_fiscalizacion=None,
                tiempo_respuesta_horas=None,
            ),
            IncidenteOut(
                id=3,
                codigo_alerta="ECO-HYO-1003",
                latitud=-12.0812,
                longitud=-75.1983,
                direccion_referencia="Av. 9 de Diciembre y Av. Próceres",
                distrito="Chilca",
                tipo_residuo=TipoResiduo.ESCOMBROS,
                gravedad=GravedadIncidente.ALTA,
                detalles="Descarga no autorizada de 2 camiones de desmonte y concreto obstruyendo la berma central.",
                evidencia_url="https://images.unsplash.com/photo-1590496793929-36417d3117de?auto=format&fit=crop&w=600&q=80",
                estado=EstadoIncidente.EN_PROCESO,
                fecha_registro=base_time + timedelta(hours=14),
                fecha_atencion=None,
                observaciones_fiscalizacion="Brigada de limpieza y volquete municipal asignados en ruta.",
                tiempo_respuesta_horas=None,
            ),
            IncidenteOut(
                id=4,
                codigo_alerta="ECO-HYO-1004",
                latitud=-12.0421,
                longitud=-75.2289,
                direccion_referencia="Subida Quebrada Honda, vía a San Pedro",
                distrito="El Tambo",
                tipo_residuo=TipoResiduo.LLANTAS,
                gravedad=GravedadIncidente.ALTA,
                detalles="Más de 40 neumáticos fuera de uso abandonados en la quebrada con riesgo de quema ilegal.",
                evidencia_url="https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?auto=format&fit=crop&w=600&q=80",
                estado=EstadoIncidente.RESUELTO,
                fecha_registro=base_time - timedelta(days=1),
                fecha_atencion=base_time - timedelta(days=1) + timedelta(hours=4),
                observaciones_fiscalizacion="Retiro completado por personal de medio ambiente y trasladado a centro de acopio.",
                tiempo_respuesta_horas=4.0,
            ),
            IncidenteOut(
                id=5,
                codigo_alerta="ECO-HYO-1005",
                latitud=-12.0734,
                longitud=-75.2072,
                direccion_referencia="Exteriores Mercado Mayorista, Av. Huancavelica",
                distrito="Huancayo Centro",
                tipo_residuo=TipoResiduo.ORGANICOS,
                gravedad=GravedadIncidente.MEDIA,
                detalles="Cúmulo de residuos vegetales y cáscaras en descomposición generando lixiviados y malos olores.",
                evidencia_url="https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&w=600&q=80",
                estado=EstadoIncidente.RESUELTO,
                fecha_registro=base_time - timedelta(days=1) + timedelta(hours=6),
                fecha_atencion=base_time - timedelta(days=1) + timedelta(hours=9),
                observaciones_fiscalizacion="Lavado y desinfección de calzada realizado con cisternas municipales.",
                tiempo_respuesta_horas=3.0,
            ),
            IncidenteOut(
                id=6,
                codigo_alerta="ECO-HYO-1006",
                latitud=-12.0589,
                longitud=-75.2410,
                direccion_referencia="Margen izquierda Río Mantaro, Puente Comuneros II",
                distrito="Pilcomayo",
                tipo_residuo=TipoResiduo.DOMICILIARIOS,
                gravedad=GravedadIncidente.ALTA,
                detalles="Microbasural espontáneo con bolsas de residuos domiciliarios y colchones cerca al puente.",
                evidencia_url="https://images.unsplash.com/photo-1605600659908-0ef719419d41?auto=format&fit=crop&w=600&q=80",
                estado=EstadoIncidente.PENDIENTE,
                fecha_registro=base_time + timedelta(hours=22),
                fecha_atencion=None,
                observaciones_fiscalizacion=None,
                tiempo_respuesta_horas=None,
            ),
        ]
        self._memory_cache = demo_items

    def ensure_table(self) -> bool:
        """Crea la tabla en SQL Server si no existe todavía con control de tiempo de espera."""
        if self._table_initialized and self._db_available:
            return True

        ahora = time.time()
        # Cooldown de 45s si la BD no estaba disponible para evitar demoras por timeout de ODBC
        if self._db_available is False and (ahora - self._last_db_check < 45):
            return False

        self._last_db_check = ahora
        try:
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("""
                    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='IncidenteAmbiental' AND xtype='U')
                    BEGIN
                        CREATE TABLE IncidenteAmbiental (
                            id INT IDENTITY(1,1) PRIMARY KEY,
                            codigo_alerta NVARCHAR(50) NOT NULL UNIQUE,
                            latitud FLOAT NOT NULL,
                            longitud FLOAT NOT NULL,
                            direccion_referencia NVARCHAR(255) NOT NULL,
                            distrito NVARCHAR(100) NOT NULL,
                            tipo_residuo NVARCHAR(100) NOT NULL,
                            gravedad NVARCHAR(50) NOT NULL DEFAULT 'Media',
                            detalles NVARCHAR(MAX) NOT NULL,
                            evidencia_url NVARCHAR(MAX) NULL,
                            estado NVARCHAR(50) NOT NULL DEFAULT 'Pendiente',
                            fecha_registro DATETIME2 NOT NULL DEFAULT GETDATE(),
                            fecha_atencion DATETIME2 NULL,
                            observaciones_fiscalizacion NVARCHAR(MAX) NULL
                        );
                    END
                """)
            self._table_initialized = True
            self._db_available = True
            return True
        except Exception as e:
            self._db_available = False
            logger.warning("SQL Server no disponible en este momento (%s), operando con almacenamiento resiliente.", e)
            return False

    def list(
        self,
        estado: str | None = None,
        tipo_residuo: str | None = None,
        distrito: str | None = None,
    ) -> list[IncidenteOut]:
        """Obtiene la lista de incidentes aplicando filtros opcionales."""
        if self.ensure_table():
            try:
                query = """
                    SELECT id, codigo_alerta, latitud, longitud, direccion_referencia,
                           distrito, tipo_residuo, gravedad, detalles, evidencia_url,
                           estado, fecha_registro, fecha_atencion, observaciones_fiscalizacion
                    FROM IncidenteAmbiental
                    WHERE 1=1
                """
                params: list[str] = []
                if estado:
                    query += " AND estado = ?"
                    params.append(estado)
                if tipo_residuo:
                    query += " AND tipo_residuo = ?"
                    params.append(tipo_residuo)
                if distrito:
                    query += " AND distrito = ?"
                    params.append(distrito)

                query += " ORDER BY fecha_registro DESC"

                with get_db_cursor() as cursor:
                    cursor.execute(query, tuple(params))
                    rows = cursor.fetchall()
                    if rows:
                        results: list[IncidenteOut] = []
                        for row in rows:
                            f_reg = row[11]
                            f_ate = row[12]
                            t_resp = None
                            if f_ate and f_reg:
                                delta = f_ate - f_reg
                                t_resp = round(delta.total_seconds() / 3600, 2)
                            results.append(
                                IncidenteOut(
                                    id=int(row[0]),
                                    codigo_alerta=str(row[1]),
                                    latitud=float(row[2]),
                                    longitud=float(row[3]),
                                    direccion_referencia=str(row[4]),
                                    distrito=str(row[5]),
                                    tipo_residuo=TipoResiduo(str(row[6])),
                                    gravedad=GravedadIncidente(str(row[7])),
                                    detalles=str(row[8]),
                                    evidencia_url=str(row[9]) if row[9] else None,
                                    estado=EstadoIncidente(str(row[10])),
                                    fecha_registro=f_reg,
                                    fecha_atencion=f_ate,
                                    observaciones_fiscalizacion=str(row[13]) if row[13] else None,
                                    tiempo_respuesta_horas=t_resp,
                                )
                            )
                        return results
            except Exception as e:
                logger.warning("Fallo en consulta SQL Server list: %s. Usando memoria.", e)

        # Fallback a caché en memoria
        filtered = self._memory_cache
        if estado:
            filtered = [i for i in filtered if i.estado.value == estado]
        if tipo_residuo:
            filtered = [i for i in filtered if i.tipo_residuo.value == tipo_residuo]
        if distrito:
            filtered = [i for i in filtered if distrito.lower() in i.distrito.lower()]
        return sorted(filtered, key=lambda x: x.fecha_registro, reverse=True)

    def get_by_id(self, incidente_id: int) -> IncidenteOut | None:
        """Obtiene un incidente por su ID."""
        if self.ensure_table():
            try:
                with get_db_cursor() as cursor:
                    cursor.execute("""
                        SELECT id, codigo_alerta, latitud, longitud, direccion_referencia,
                               distrito, tipo_residuo, gravedad, detalles, evidencia_url,
                               estado, fecha_registro, fecha_atencion, observaciones_fiscalizacion
                        FROM IncidenteAmbiental
                        WHERE id = ?
                    """, (incidente_id,))
                    row = cursor.fetchone()
                    if row:
                        f_reg = row[11]
                        f_ate = row[12]
                        t_resp = None
                        if f_ate and f_reg:
                            delta = f_ate - f_reg
                            t_resp = round(delta.total_seconds() / 3600, 2)
                        return IncidenteOut(
                            id=int(row[0]),
                            codigo_alerta=str(row[1]),
                            latitud=float(row[2]),
                            longitud=float(row[3]),
                            direccion_referencia=str(row[4]),
                            distrito=str(row[5]),
                            tipo_residuo=TipoResiduo(str(row[6])),
                            gravedad=GravedadIncidente(str(row[7])),
                            detalles=str(row[8]),
                            evidencia_url=str(row[9]) if row[9] else None,
                            estado=EstadoIncidente(str(row[10])),
                            fecha_registro=f_reg,
                            fecha_atencion=f_ate,
                            observaciones_fiscalizacion=str(row[13]) if row[13] else None,
                            tiempo_respuesta_horas=t_resp,
                        )
            except Exception as e:
                logger.warning("Fallo en consulta SQL Server get_by_id: %s", e)

        for item in self._memory_cache:
            if item.id == incidente_id:
                return item
        return None

    def create(
        self,
        datos: IncidenteCreate,
        codigo_alerta: str,
        gravedad: GravedadIncidente,
    ) -> IncidenteOut:
        """Inserta un nuevo reporte ciudadano en SQL Server con pyodbc."""
        fecha_ahora = datetime.now()

        if self.ensure_table():
            try:
                with get_db_cursor(commit=True) as cursor:
                    cursor.execute("""
                        INSERT INTO IncidenteAmbiental (
                            codigo_alerta, latitud, longitud, direccion_referencia,
                            distrito, tipo_residuo, gravedad, detalles, evidencia_url,
                            estado, fecha_registro
                        )
                        OUTPUT INSERTED.id, INSERTED.fecha_registro
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        codigo_alerta,
                        datos.latitud,
                        datos.longitud,
                        datos.direccion_referencia,
                        datos.distrito,
                        datos.tipo_residuo.value,
                        gravedad.value,
                        datos.detalles,
                        datos.evidencia_url,
                        EstadoIncidente.PENDIENTE.value,
                        fecha_ahora,
                    ))
                    row = cursor.fetchone()
                    if row:
                        nuevo = IncidenteOut(
                            id=int(row[0]),
                            codigo_alerta=codigo_alerta,
                            latitud=datos.latitud,
                            longitud=datos.longitud,
                            direccion_referencia=datos.direccion_referencia,
                            distrito=datos.distrito,
                            tipo_residuo=datos.tipo_residuo,
                            gravedad=gravedad,
                            detalles=datos.detalles,
                            evidencia_url=datos.evidencia_url,
                            estado=EstadoIncidente.PENDIENTE,
                            fecha_registro=row[1],
                            fecha_atencion=None,
                            observaciones_fiscalizacion=None,
                            tiempo_respuesta_horas=None,
                        )
                        self._memory_cache.insert(0, nuevo)
                        return nuevo
            except Exception as e:
                logger.warning("Fallo al insertar en SQL Server: %s. Almacenando en memoria.", e)

        # Fallback en memoria
        new_id = (max([i.id for i in self._memory_cache], default=0)) + 1
        nuevo = IncidenteOut(
            id=new_id,
            codigo_alerta=codigo_alerta,
            latitud=datos.latitud,
            longitud=datos.longitud,
            direccion_referencia=datos.direccion_referencia,
            distrito=datos.distrito,
            tipo_residuo=datos.tipo_residuo,
            gravedad=gravedad,
            detalles=datos.detalles,
            evidencia_url=datos.evidencia_url,
            estado=EstadoIncidente.PENDIENTE,
            fecha_registro=fecha_ahora,
            fecha_atencion=None,
            observaciones_fiscalizacion=None,
            tiempo_respuesta_horas=None,
        )
        self._memory_cache.insert(0, nuevo)
        return nuevo

    def update_status(
        self,
        incidente_id: int,
        nuevo_estado: EstadoIncidente,
        observaciones: str | None = None,
    ) -> IncidenteOut | None:
        """Actualiza el estado y observaciones de un incidente."""
        fecha_atencion = datetime.now() if nuevo_estado == EstadoIncidente.RESUELTO else None

        if self.ensure_table():
            try:
                with get_db_cursor(commit=True) as cursor:
                    if fecha_atencion:
                        cursor.execute("""
                            UPDATE IncidenteAmbiental
                            SET estado = ?, fecha_atencion = ?, observaciones_fiscalizacion = ?
                            WHERE id = ?
                        """, (nuevo_estado.value, fecha_atencion, observaciones, incidente_id))
                    else:
                        cursor.execute("""
                            UPDATE IncidenteAmbiental
                            SET estado = ?, observaciones_fiscalizacion = ?
                            WHERE id = ?
                        """, (nuevo_estado.value, observaciones, incidente_id))
            except Exception as e:
                logger.warning("Fallo al actualizar SQL Server: %s", e)

        for idx, item in enumerate(self._memory_cache):
            if item.id == incidente_id:
                t_resp = None
                if nuevo_estado == EstadoIncidente.RESUELTO:
                    f_ate = fecha_atencion or datetime.now()
                    delta = f_ate - item.fecha_registro
                    t_resp = round(delta.total_seconds() / 3600, 2)
                else:
                    f_ate = None

                actualizado = item.model_copy(update={
                    "estado": nuevo_estado,
                    "fecha_atencion": f_ate,
                    "observaciones_fiscalizacion": observaciones or item.observaciones_fiscalizacion,
                    "tiempo_respuesta_horas": t_resp,
                })
                self._memory_cache[idx] = actualizado
                return actualizado

        return self.get_by_id(incidente_id)


incidente_repository = IncidenteRepository()
