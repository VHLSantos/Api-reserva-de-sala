from __future__ import annotations

from datetime import datetime
from domain.usuario import Usuario
from domain.sala import Sala
from domain.reserva import Reserva
from repositories.memory import db


MAX_RESERVAS_ATIVAS_POR_DIA = 2
MAX_DURACAO_HORAS = 2


def _parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_time(value: str):
    return datetime.strptime(value, "%H:%M").time()


def _parse_datetime(data: str, hora: str):
    return datetime.combine(_parse_date(data), _parse_time(hora))


def _usuario_to_dict(usuario: Usuario) -> dict:
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email}


def _sala_to_dict(sala: Sala) -> dict:
    return {"id": sala.id, "nome": sala.nome, "capacidade": sala.capacidade, "bloco": sala.bloco}


def _reserva_to_dict(reserva: Reserva) -> dict:
    return reserva.to_dict()


def criar_usuario(nome: str, email: str):
    if not nome or not nome.strip():
        raise ValueError("Nome é obrigatório.")
    if not email or not str(email).strip():
        raise ValueError("Email é obrigatório.")

    email_normalizado = email.strip().lower()
    for usuario in db.usuarios.values():
        if usuario.email.lower() == email_normalizado:
            raise ValueError("Email duplicado.")

    usuario = Usuario(id=db.next_usuario_id, nome=nome.strip(), email=email_normalizado)
    db.usuarios[usuario.id] = usuario
    db.next_usuario_id += 1
    return _usuario_to_dict(usuario)


def listar_usuarios():
    return [_usuario_to_dict(u) for u in db.usuarios.values()]


def criar_sala(nome: str, capacidade: int, bloco: str):
    if not nome or not nome.strip():
        raise ValueError("Nome da sala é obrigatório.")
    if capacidade is None or capacidade <= 0:
        raise ValueError("Capacidade deve ser maior que zero.")
    if not bloco or not bloco.strip():
        raise ValueError("Bloco é obrigatório.")

    sala = Sala(id=db.next_sala_id, nome=nome.strip(), capacidade=capacidade, bloco=bloco.strip())
    db.salas[sala.id] = sala
    db.next_sala_id += 1
    return _sala_to_dict(sala)


def listar_salas():
    return [_sala_to_dict(s) for s in db.salas.values()]


def _validar_reserva_nova(usuario_id: int, sala_id: int, data: str, hora_inicio: str, hora_fim: str):
    if usuario_id not in db.usuarios:
        raise ValueError("Usuário não encontrado.")
    if sala_id not in db.salas:
        raise ValueError("Sala não encontrada.")

    inicio = _parse_datetime(data, hora_inicio)
    fim = _parse_datetime(data, hora_fim)
    now = datetime.now()

    if inicio < now:
        raise ValueError("Não é permitido reservar para horário passado.")
    if fim <= inicio:
        raise ValueError("Hora final deve ser maior que hora inicial.")

    duracao_horas = (fim - inicio).total_seconds() / 3600
    if duracao_horas > MAX_DURACAO_HORAS:
        raise ValueError("A duração máxima de uma reserva é de 2 horas.")

    reserva_temporaria = Reserva(
        id=0,
        usuario_id=usuario_id,
        sala_id=sala_id,
        data=data,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
    )

    reservas_mesma_sala = [
        r for r in db.reservas.values()
        if r.sala_id == sala_id and r.data == data and r.status != "canceled"
    ]
    for reserva in reservas_mesma_sala:
        if reserva_temporaria.conflita_com(reserva):
            raise ValueError("Conflito de horário para a mesma sala.")

    reservas_mesmo_usuario = [
        r for r in db.reservas.values()
        if r.usuario_id == usuario_id and r.data == data and r.status != "canceled"
    ]
    for reserva in reservas_mesmo_usuario:
        if reserva_temporaria.conflita_com(reserva):
            raise ValueError("Conflito de horário para o mesmo usuário.")

    reservas_ativas_dia = [
        r for r in reservas_mesmo_usuario if r.status == "active"
    ]
    if len(reservas_ativas_dia) >= MAX_RESERVAS_ATIVAS_POR_DIA:
        raise ValueError("Um usuário pode ter no máximo 2 reservas ativas por dia.")


def criar_reserva(usuario_id: int, sala_id: int, data: str, hora_inicio: str, hora_fim: str):
    _validar_reserva_nova(usuario_id, sala_id, data, hora_inicio, hora_fim)

    reserva = Reserva(
        id=db.next_reserva_id,
        usuario_id=usuario_id,
        sala_id=sala_id,
        data=data,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
    )
    db.reservas[reserva.id] = reserva
    db.next_reserva_id += 1
    return _reserva_to_dict(reserva)


def listar_reservas():
    return [_reserva_to_dict(r) for r in db.reservas.values()]


def listar_reservas_usuario(usuario_id: int):
    if usuario_id not in db.usuarios:
        raise ValueError("Usuário não encontrado.")
    return [_reserva_to_dict(r) for r in db.reservas.values() if r.usuario_id == usuario_id]


def buscar_reserva(reserva_id: int):
    reserva = db.reservas.get(reserva_id)
    if not reserva:
        raise ValueError("Reserva não encontrada.")
    return _reserva_to_dict(reserva)


def cancelar_reserva(reserva_id: int):
    reserva = db.reservas.get(reserva_id)
    if not reserva:
        raise ValueError("Reserva não encontrada.")
    reserva.cancelar()
    return _reserva_to_dict(reserva)


def finalizar_reserva(reserva_id: int, hora_atual: str):
    reserva = db.reservas.get(reserva_id)
    if not reserva:
        raise ValueError("Reserva não encontrada.")
    reserva.finalizar(hora_atual)
    return _reserva_to_dict(reserva)
