from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(..., min_length=3, max_length=150, examples=["usuario@ejemplo.com"])
    password: str = Field(..., min_length=6, max_length=100, examples=["claveSecreta1"])


class UserLogin(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(..., min_length=1, examples=["usuario@ejemplo.com"])
    password: str = Field(..., min_length=1, examples=["claveSecreta1"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str


class UserResponse(BaseModel):
    id_usuario: int
    email: str
