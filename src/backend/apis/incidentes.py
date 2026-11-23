from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.schemas.incidentes import (
    DashboardMetricas,
    IncidenteCreate,
    IncidenteOut,
    IncidenteUpdate,
)
from backend.services.incidentes import IncidenteService, incidente_service

router = APIRouter(prefix="/incidentes", tags=["incidentes"])


def get_incidente_service() -> IncidenteService:
    return incidente_service


ServiceDep = Annotated[IncidenteService, Depends(get_incidente_service)]


@router.post(
    "",
    response_model=IncidenteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar reporte ciudadano de Alerta Verde",
    description="Permite a los ciudadanos enviar un foco de contaminación con geolocalización, residuo y evidencia.",
)
def registrar_reporte(
    datos: IncidenteCreate,
    service: ServiceDep,
) -> IncidenteOut:
    return service.registrar_reporte(datos)


@router.get(
    "",
    response_model=list[IncidenteOut],
    summary="Listar incidentes ambientales",
    description="Retorna la bandeja de incidentes para el panel de fiscalización con filtros opcionales.",
)
def listar_incidentes(
    service: ServiceDep,
    estado: Annotated[str | None, Query(description="Filtrar por estado (Pendiente, En proceso, Resuelto)")] = None,
    tipo_residuo: Annotated[str | None, Query(description="Filtrar por tipo de residuo")] = None,
    distrito: Annotated[str | None, Query(description="Filtrar por distrito (El Tambo, Chilca, etc.)")] = None,
) -> list[IncidenteOut]:
    return service.listar_incidentes(estado=estado, tipo_residuo=tipo_residuo, distrito=distrito)


@router.get(
    "/metricas/dashboard",
    response_model=DashboardMetricas,
    summary="Obtener métricas y KPIs del Centro de Monitoreo",
    description="Calcula en tiempo real Total Alertas, Puntos Críticos, Alertas Atendidas y Tiempo Promedio.",
)
def obtener_metricas(service: ServiceDep) -> DashboardMetricas:
    return service.obtener_metricas_dashboard()


@router.get(
    "/{id_incidente}",
    response_model=IncidenteOut,
    summary="Obtener detalle de un incidente",
    description="Consulta la información completa de un incidente por su identificador.",
)
def obtener_incidente(
    id_incidente: int,
    service: ServiceDep,
) -> IncidenteOut:
    incidente = service.obtener_incidente(id_incidente)
    if not incidente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el reporte con ID {id_incidente}",
        )
    return incidente


@router.patch(
    "/{id_incidente}/estado",
    response_model=IncidenteOut,
    summary="Actualizar estado del incidente (Fiscalización)",
    description="Permite marcar un incidente como 'En proceso' o 'Resuelto' y agregar notas de remediación.",
)
def actualizar_estado(
    id_incidente: int,
    datos: IncidenteUpdate,
    service: ServiceDep,
) -> IncidenteOut:
    actualizado = service.actualizar_estado(id_incidente, datos)
    if not actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el reporte con ID {id_incidente}",
        )
    return actualizado
