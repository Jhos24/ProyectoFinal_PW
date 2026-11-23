from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TipoResiduo(str, Enum):
    PLASTICOS = "Plásticos y Microplásticos"
    ESCOMBROS = "Escombros y Construcción"
    ORGANICOS = "Orgánicos y Agrícolas"
    PELIGROSOS = "Residuos Peligrosos y Hospitalarios"
    DOMICILIARIOS = "Basura Domiciliaria Voluminosa"
    LLANTAS = "Neumáticos y Llantas"
    OTROS = "Otros Residuos Contaminantes"


class EstadoIncidente(str, Enum):
    PENDIENTE = "Pendiente"
    EN_PROCESO = "En proceso"
    RESUELTO = "Resuelto"


class GravedadIncidente(str, Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    CRITICA = "Crítica"


class IncidenteBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )

    latitud: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitud GPS del foco contaminante.",
        examples=[-12.0653],
    )
    longitud: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitud GPS del foco contaminante.",
        examples=[-75.2049],
    )
    direccion_referencia: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Dirección o punto de referencia en Huancayo.",
        examples=["Av. Ferrocarril c/ Jr. Puno, Huancayo Centro"],
    )
    distrito: str = Field(
        default="Huancayo",
        min_length=2,
        max_length=100,
        description="Distrito del foco (El Tambo, Chilca, Huancayo, Pilcomayo, etc.).",
        examples=["Huancayo"],
    )
    tipo_residuo: TipoResiduo = Field(
        ...,
        description="Categoría del residuo contaminante identificado.",
        examples=[TipoResiduo.PLASTICOS],
    )
    detalles: str = Field(
        ...,
        min_length=5,
        max_length=1500,
        description="Descripción detallada de la contaminación y su impacto.",
        examples=["Acumulación excesiva de plásticos y botellas tapando la cuneta de desagüe fluvial."],
    )
    evidencia_url: str | None = Field(
        default=None,
        description="URL, path o Data URI (base64) de la fotografía de evidencia.",
    )


class IncidenteCreate(IncidenteBase):
    """Datos enviados por el ciudadano en el formulario Alerta Verde."""
    pass


class IncidenteUpdate(BaseModel):
    """Datos actualizables desde el Panel de Fiscalización."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )

    estado: EstadoIncidente | None = Field(
        default=None,
        description="Nuevo estado del incidente.",
    )
    observaciones_fiscalizacion: str | None = Field(
        default=None,
        max_length=1000,
        description="Comentarios, orden de remediación o resolución del fiscalizador.",
    )


class IncidenteOut(IncidenteBase):
    """Respuesta con la información completa del incidente."""
    id: int = Field(..., description="Identificador único en base de datos.")
    codigo_alerta: str = Field(..., description="Código cívico legible de seguimiento (ej. ECO-HYO-1001).")
    gravedad: GravedadIncidente = Field(
        default=GravedadIncidente.MEDIA,
        description="Nivel de gravedad asignado según el tipo de residuo.",
    )
    estado: EstadoIncidente = Field(
        default=EstadoIncidente.PENDIENTE,
        description="Estado actual del reporte ambiental.",
    )
    fecha_registro: datetime = Field(..., description="Fecha y hora de creación del reporte.")
    fecha_atencion: datetime | None = Field(
        default=None,
        description="Fecha y hora en que fue marcado como Resuelto.",
    )
    observaciones_fiscalizacion: str | None = Field(
        default=None,
        description="Notas del equipo de fiscalización ambiental.",
    )
    tiempo_respuesta_horas: float | None = Field(
        default=None,
        description="Tiempo en horas desde el registro hasta la atención.",
    )


class DashboardMetricas(BaseModel):
    """Métricas KPI para el Centro de Monitoreo de Fiscalización."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )

    total_alertas: int = Field(..., description="Total de alertas recibidas.")
    puntos_criticos: int = Field(..., description="Alertas pendientes con gravedad Alta o Crítica.")
    alertas_atendidas: int = Field(..., description="Total de alertas resueltas.")
    tiempo_promedio_respuesta: str = Field(..., description="Tiempo promedio de remediación (ej: '3.8 horas').")
    alertas_pendientes: int = Field(..., description="Alertas pendientes de inspección.")
    alertas_en_proceso: int = Field(..., description="Alertas actualmente bajo intervención.")
    distribucion_residuos: dict[str, int] = Field(default_factory=dict)
    distribucion_distritos: dict[str, int] = Field(default_factory=dict)
