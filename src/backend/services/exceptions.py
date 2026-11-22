class PersonaNotFoundError(Exception):
    """No existe una persona con el DNI solicitado."""

    def __init__(self, dni: str) -> None:
        self.dni = dni
        super().__init__(f"No existe una persona con DNI '{dni}'.")


class PersonaAlreadyExistsError(Exception):
    """Ya hay una persona registrada con ese DNI."""

    def __init__(self, dni: str) -> None:
        self.dni = dni
        super().__init__(f"Ya existe una persona con DNI '{dni}'.")
