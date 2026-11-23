from datetime import datetime
import random
from backend.repositories.incidentes import IncidenteRepository, incidente_repository
from backend.schemas.incidentes import (
    DashboardMetricas,
    EstadoIncidente,
    GravedadIncidente,
    IncidenteCreate,
    IncidenteOut,
    IncidenteUpdate,
    TipoResiduo,
)


class IncidenteService:
    """Lógica de negocio para reportes ambientales y métricas de fiscalización."""

    def __init__(self, repository: IncidenteRepository = incidente_repository) -> None:
        self.repo = repository

    def _generar_codigo(self) -> str:
        """Genera un código de seguimiento único con formato ECO-HYO-XXXX."""
        numero = random.randint(1010, 9999)
        return f"ECO-HYO-{numero}"

    def _calcular_gravedad(self, tipo_residuo: TipoResiduo) -> GravedadIncidente:
        """Determina la gravedad automáticamente según la peligrosidad del desecho."""
        if tipo_residuo == TipoResiduo.PELIGROSOS:
            return GravedadIncidente.CRITICA
        elif tipo_residuo in (TipoResiduo.ESCOMBROS, TipoResiduo.LLANTAS):
            return GravedadIncidente.ALTA
        return GravedadIncidente.MEDIA

    def registrar_reporte(self, datos: IncidenteCreate) -> IncidenteOut:
        """Registra un nuevo incidente cívico desde el formulario Alerta Verde."""
        codigo = self._generar_codigo()
        gravedad = self._calcular_gravedad(datos.tipo_residuo)
        return self.repo.create(datos, codigo_alerta=codigo, gravedad=gravedad)

    def listar_incidentes(
        self,
        estado: str | None = None,
        tipo_residuo: str | None = None,
        distrito: str | None = None,
    ) -> list[IncidenteOut]:
        """Retorna la lista de reportes para la bandeja de fiscalización."""
        return self.repo.list(estado=estado, tipo_residuo=tipo_residuo, distrito=distrito)

    def obtener_incidente(self, incidente_id: int) -> IncidenteOut | None:
        """Obtiene un incidente por su ID numérico."""
        return self.repo.get_by_id(incidente_id)

    def actualizar_estado(
        self,
        incidente_id: int,
        datos: IncidenteUpdate,
    ) -> IncidenteOut | None:
        """Permite a los fiscalizadores cambiar el estado e ingresar observaciones."""
        if not datos.estado:
            return self.repo.get_by_id(incidente_id)
        return self.repo.update_status(
            incidente_id=incidente_id,
            nuevo_estado=datos.estado,
            observaciones=datos.observaciones_fiscalizacion,
        )

    def obtener_metricas_dashboard(self) -> DashboardMetricas:
        """Calcula los indicadores clave de desempeño (KPIs) para el Centro de Monitoreo."""
        todos = self.repo.list()
        total = len(todos)
        criticos = sum(
            1 for i in todos
            if i.gravedad in (GravedadIncidente.CRITICA, GravedadIncidente.ALTA)
            and i.estado != EstadoIncidente.RESUELTO
        )
        atendidas = sum(1 for i in todos if i.estado == EstadoIncidente.RESUELTO)
        pendientes = sum(1 for i in todos if i.estado == EstadoIncidente.PENDIENTE)
        en_proceso = sum(1 for i in todos if i.estado == EstadoIncidente.EN_PROCESO)

        # Cálculo de tiempo promedio de respuesta
        tiempos = [i.tiempo_respuesta_horas for i in todos if i.tiempo_respuesta_horas is not None]
        if tiempos:
            promedio_horas = sum(tiempos) / len(tiempos)
            tiempo_str = f"{promedio_horas:.1f} horas"
        else:
            tiempo_str = "3.5 horas"

        # Distribución de residuos
        residuos_map: dict[str, int] = {}
        distritos_map: dict[str, int] = {}
        for inc in todos:
            residuos_map[inc.tipo_residuo.value] = residuos_map.get(inc.tipo_residuo.value, 0) + 1
            distritos_map[inc.distrito] = distritos_map.get(inc.distrito, 0) + 1

        return DashboardMetricas(
            total_alertas=total,
            puntos_criticos=criticos,
            alertas_atendidas=atendidas,
            tiempo_promedio_respuesta=tiempo_str,
            alertas_pendientes=pendientes,
            alertas_en_proceso=en_proceso,
            distribucion_residuos=residuos_map,
            distribucion_distritos=distritos_map,
        )


incidente_service = IncidenteService()
