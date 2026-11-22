import unittest
from unittest.mock import MagicMock
from backend.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from backend.repositories.usuarios import UsuarioRecord, UsuarioRepository
from backend.schemas.auth import UserLogin, UserRegister
from backend.services.auth import AuthService


class TestSecurity(unittest.TestCase):
    def test_hash_and_verify_password(self):
        password = "miPasswordSeguro123"
        hashed = hash_password(password)

        self.assertNotEqual(password, hashed)
        self.assertTrue(hashed.startswith("$argon2"))
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("otroPasswordErroneo", hashed))

    def test_jwt_create_and_decode(self):
        data = {"sub": "usuario@correo.com", "uid": 1}
        token = create_access_token(data)

        self.assertIsInstance(token, str)
        decoded = decode_access_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], "usuario@correo.com")
        self.assertEqual(decoded["uid"], 1)
        self.assertIn("exp", decoded)

    def test_decode_invalid_token(self):
        decoded = decode_access_token("token.invalido.123")
        self.assertIsNone(decoded)


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock(spec=UsuarioRepository)
        self.service = AuthService(repository=self.mock_repo)

    def test_registrar_nuevo_usuario(self):
        self.mock_repo.exists.return_value = False
        self.mock_repo.create.return_value = UsuarioRecord(
            id_usuario=1,
            email="nuevo@correo.com",
            password="fakehash",
        )

        datos = UserRegister(email="nuevo@correo.com", password="password123")
        token = self.service.registrar(datos)

        self.assertEqual(token.email, "nuevo@correo.com")
        self.assertIsNotNone(token.access_token)
        self.mock_repo.exists.assert_called_once_with("nuevo@correo.com")
        self.mock_repo.create.assert_called_once()

    def test_login_exitoso(self):
        hashed = hash_password("secreto123")
        self.mock_repo.get_by_email.return_value = UsuarioRecord(
            id_usuario=1,
            email="juan@correo.com",
            password=hashed,
        )

        datos = UserLogin(email="juan@correo.com", password="secreto123")
        token = self.service.login(datos)

        self.assertEqual(token.email, "juan@correo.com")
        self.assertIsNotNone(token.access_token)

    def test_login_fallido_password_incorrecto(self):
        hashed = hash_password("secreto123")
        self.mock_repo.get_by_email.return_value = UsuarioRecord(
            id_usuario=1,
            email="juan@correo.com",
            password=hashed,
        )

        datos = UserLogin(email="juan@correo.com", password="passwordErroneo")
        with self.assertRaises(Exception) as ctx:
            self.service.login(datos)
        self.assertEqual(ctx.exception.status_code, 401)
