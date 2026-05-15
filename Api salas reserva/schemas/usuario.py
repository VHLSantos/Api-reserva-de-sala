from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr

class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: EmailStr

    model_config = {"from_attributes": True}
