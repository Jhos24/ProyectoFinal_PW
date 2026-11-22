from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.core.security import decode_access_token
from backend.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from backend.services.auth import AuthService, auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
security_scheme = HTTPBearer(auto_error=False)


def get_current_user_email(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
) -> str:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación no proporcionado.",
        )
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
        )
    return str(payload["sub"])


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
)
def register(datos: UserRegister) -> Token:
    return auth_service.registrar(datos)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión y obtener token JWT",
)
def login(datos: UserLogin) -> Token:
    return auth_service.login(datos)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener información del usuario autenticado",
)
def get_me(current_email: Annotated[str, Depends(get_current_user_email)]) -> UserResponse:
    return auth_service.obtener_perfil(current_email)
