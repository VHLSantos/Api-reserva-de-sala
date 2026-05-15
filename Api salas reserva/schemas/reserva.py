from pydantic import BaseModel

class ReservaCreate(BaseModel):
    usuario_id: int
    sala_id: int
    data: str
    hora_inicio: str
    hora_fim: str

class ReservaOut(BaseModel):
    id: int
    usuario_id: int
    sala_id: int
    data: str
    hora_inicio: str
    hora_fim: str
    status: str

    model_config = {"from_attributes": True}
