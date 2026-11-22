from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from backend.schemas.personas import Persona, PersonaCreate, PersonaUpdate
from backend.services.personas import PersonaService, persona_service

router = APIRouter(prefix="/personas", tags=["personas"])

DniPath = Annotated[
    str,
    Path(pattern=r"^\d{8}$", description="DNI de la persona (8 dígitos)."),
]

def get_persona_service() -> PersonaService:
    return persona_service


ServiceDep = Annotated[PersonaService, Depends(get_persona_service)]


@router.get("", response_model=list[Persona], summary="Listar personas")
def listar_personas(service: ServiceDep) -> list[Persona]:
    return service.listar()


@router.get("/{dni}", response_model=Persona, summary="Obtener una persona por DNI")
def obtener_persona(dni: DniPath, service: ServiceDep) -> Persona:
    return service.obtener(dni)


@router.post(
    "",
    response_model=Persona,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una persona",
)
def crear_persona(datos: PersonaCreate, service: ServiceDep) -> Persona:
    return service.crear(datos)


@router.put("/{dni}", response_model=Persona, summary="Actualizar una persona")
def actualizar_persona(
    dni: DniPath, datos: PersonaUpdate, service: ServiceDep
) -> Persona:
    return service.actualizar(dni, datos)


@router.delete(
    "/{dni}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una persona",
)
def eliminar_persona(dni: DniPath, service: ServiceDep) -> None:
    service.eliminar(dni)
