from fastapi import APIRouter, HTTPException, status
from schemas.usuario import UsuarioCreate, UsuarioOut
from services.reserva_service import criar_usuario, listar_usuarios

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario_route(data: UsuarioCreate):
    try:
        return criar_usuario(data.nome, data.email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios_route():
    return listar_usuarios()
