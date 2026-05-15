from fastapi import APIRouter, HTTPException, status
from schemas.sala import SalaCreate, SalaOut
from services.reserva_service import criar_sala, listar_salas

router = APIRouter(prefix="/salas", tags=["Salas"])


@router.post("", response_model=SalaOut, status_code=status.HTTP_201_CREATED)
def criar_sala_route(data: SalaCreate):
    try:
        return criar_sala(data.nome, data.capacidade, data.bloco)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[SalaOut])
def listar_salas_route():
    return listar_salas()
