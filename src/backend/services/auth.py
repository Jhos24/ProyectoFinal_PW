from fastapi import HTTPException, status
from backend.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.repositories.usuarios import UsuarioRepository, usuario_repository
from backend.schemas.auth import Token, UserLogin, UserRegister, UserResponse


class AuthService:
    """Reglas de negocio para registro y autenticación con Argon2 y JWT."""

    def __init__(self, repository: UsuarioRepository | None = None) -> None:
        self._repo = repository or usuario_repository

    def registrar(self, datos: UserRegister) -> Token:
        if self._repo.exists(datos.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya se encuentra registrado.",
            )

        hashed = hash_password(datos.password)
        usuario = self._repo.create(datos.email, hashed)

        token = create_access_token({"sub": usuario.email, "uid": usuario.id_usuario})
        return Token(access_token=token, email=usuario.email)

    def login(self, datos: UserLogin) -> Token:
        usuario = self._repo.get_by_email(datos.email)
        if usuario is None or not verify_password(datos.password, usuario.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas (correo o contraseña inválidos).",
            )

        token = create_access_token({"sub": usuario.email, "uid": usuario.id_usuario})
        return Token(access_token=token, email=usuario.email)

    def obtener_perfil(self, email: str) -> UserResponse:
        usuario = self._repo.get_by_email(email)
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado.",
            )
        return UserResponse(
            id_usuario=usuario.id_usuario,
            email=usuario.email,
        )


auth_service = AuthService()
