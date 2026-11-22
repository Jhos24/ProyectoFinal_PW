from datetime import date

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class PersonaBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )

    dni: str = Field(
        ...,
        pattern=r"^\d{8}$",
        description="Documento Nacional de Identidad (8 dígitos).",
        examples=["12345678"],
    )
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Ana Torres"])
    fecha_nacimiento: date = Field(..., examples=["1990-05-17"])


class PersonaCreate(PersonaBase):
    """Datos necesarios para crear una persona."""


class PersonaUpdate(BaseModel):
    """Datos modificables de una persona (el DNI no se puede cambiar)."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )

    nombre: str = Field(..., min_length=1, max_length=100, examples=["Ana Torres"])
    fecha_nacimiento: date = Field(..., examples=["1990-05-17"])


class Persona(PersonaBase):
    """Representación de una persona almacenada."""
