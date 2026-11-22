from backend.repositories.personas import PersonaRepository, persona_repository
from backend.schemas.personas import Persona, PersonaCreate, PersonaUpdate
from backend.services.exceptions import (
    PersonaAlreadyExistsError,
    PersonaNotFoundError,
)


class PersonaService:
    """Reglas de negocio del CRUD de personas."""

    def __init__(self, repository: PersonaRepository | None = None) -> None:
        self._repository = repository or persona_repository

    def listar(self) -> list[Persona]:
        return self._repository.list()

    def obtener(self, dni: str) -> Persona:
        persona = self._repository.get(dni)
        if persona is None:
            raise PersonaNotFoundError(dni)
        return persona

    def crear(self, datos: PersonaCreate) -> Persona:
        if self._repository.exists(datos.dni):
            raise PersonaAlreadyExistsError(datos.dni)
        return self._repository.add(Persona(**datos.model_dump()))

    def actualizar(self, dni: str, datos: PersonaUpdate) -> Persona:
        persona = self._repository.update(dni, datos)
        if persona is None:
            raise PersonaNotFoundError(dni)
        return persona

    def eliminar(self, dni: str) -> None:
        if not self._repository.delete(dni):
            raise PersonaNotFoundError(dni)


persona_service = PersonaService()
