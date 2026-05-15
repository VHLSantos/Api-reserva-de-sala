from fastapi import APIRouter, HTTPException, status, Query
from schemas.reserva import ReservaCreate, ReservaOut
from services.reserva_service import (
    criar_reserva,
    listar_reservas,
    listar_reservas_usuario,
    buscar_reserva,
    cancelar_reserva,
    finalizar_reserva,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post("", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
def criar_reserva_route(data: ReservaCreate):
    try:
        return criar_reserva(data.usuario_id, data.sala_id, data.data, data.hora_inicio, data.hora_fim)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[ReservaOut])
def listar_reservas_route():
    return listar_reservas()


@router.get("/usuario/{usuario_id}", response_model=list[ReservaOut])
def listar_reservas_usuario_route(usuario_id: int):
    try:
        return listar_reservas_usuario(usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{reserva_id}", response_model=ReservaOut)
def buscar_reserva_route(reserva_id: int):
    try:
        return buscar_reserva(reserva_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{reserva_id}/cancelar", response_model=ReservaOut)
def cancelar_reserva_route(reserva_id: int):
    try:
        return cancelar_reserva(reserva_id)
    except ValueError as e:
        message = str(e)
        code = status.HTTP_404_NOT_FOUND if message == "Reserva não encontrada." else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=message)


@router.put("/{reserva_id}/finalizar", response_model=ReservaOut)
def finalizar_reserva_route(reserva_id: int, hora_atual: str = Query(..., description="Hora atual no formato HH:MM")):
    try:
        return finalizar_reserva(reserva_id, hora_atual)
    except ValueError as e:
        message = str(e)
        code = status.HTTP_404_NOT_FOUND if message == "Reserva não encontrada." else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=message)
