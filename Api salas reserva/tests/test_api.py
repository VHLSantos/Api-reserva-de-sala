from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from main import app
from repositories.memory import db

client = TestClient(app)


def setup_function():
    db.reset()


def future_date(days=1):
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")


def future_datetime(days=1, hour=10, minute=0):
    d = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    return d, f"{hour:02d}:{minute:02d}"


def test_criar_usuario():
    resp = client.post("/usuarios", json={"nome": "Ana Souza", "email": "ana@email.com"})
    assert resp.status_code == 201
    assert resp.json()["id"] == 1


def test_email_duplicado():
    client.post("/usuarios", json={"nome": "Ana Souza", "email": "ana@email.com"})
    resp = client.post("/usuarios", json={"nome": "Ana 2", "email": "ana@email.com"})
    assert resp.status_code == 400


def test_criar_sala_valida():
    resp = client.post("/salas", json={"nome": "Sala 101", "capacidade": 6, "bloco": "A"})
    assert resp.status_code == 201


def test_criar_sala_capacidade_invalida():
    resp = client.post("/salas", json={"nome": "Sala 101", "capacidade": 0, "bloco": "A"})
    assert resp.status_code == 400


def test_criar_reserva_valida():
    client.post("/usuarios", json={"nome": "Ana Souza", "email": "ana@email.com"})
    client.post("/salas", json={"nome": "Sala 101", "capacidade": 6, "bloco": "A"})
    data, hora_inicio = future_datetime(1, 14, 0)
    resp = client.post("/reservas", json={
        "usuario_id": 1,
        "sala_id": 1,
        "data": data,
        "hora_inicio": hora_inicio,
        "hora_fim": "15:30",
    })
    assert resp.status_code == 201
    assert resp.json()["status"] == "active"


def test_reserva_horario_passado():
    client.post("/usuarios", json={"nome": "Ana Souza", "email": "ana@email.com"})
    client.post("/salas", json={"nome": "Sala 101", "capacidade": 6, "bloco": "A"})
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    resp = client.post("/reservas", json={
        "usuario_id": 1,
        "sala_id": 1,
        "data": yesterday,
        "hora_inicio": "14:00",
        "hora_fim": "15:00",
    })
    assert resp.status_code == 400


def test_conflito_mesma_sala():
    client.post("/usuarios", json={"nome": "Ana Souza", "email": "ana@email.com"})
    client.post("/usuarios", json={"nome": "Bruno", "email": "bruno@email.com"})
    client.post("/salas", json={"nome": "Sala 101", "capacidade": 6, "bloco": "A"})
    data, _ = future_datetime(1, 14, 0)
    r1 = client.post("/reservas", json={
        "usuario_id": 1, "sala_id": 1, "data": data, "hora_inicio": "14:00", "hora_fim": "15:00"
    })
    assert r1.status_code == 201
    r2 = client.post("/reservas", json={
        "usuario_id": 2, "sala_id": 1, "data": data, "hora_inicio": "14:30", "hora_fim": "15:30"
    })
    assert r2.status_code == 400


def test_conflito_mesmo_usuario():
    client.post("/usuarios", json={"nome": "Ana Souza", "email": "ana@email.com"})
    client.post("/salas", json={"nome": "Sala 101", "capacidade": 6, "bloco": "A"})
    client.post("/salas", json={"nome": "Sala 102", "capacidade": 6, "bloco": "A"})
    data, _ = future_datetime(1, 14, 0)
    r1 = client.post("/reservas", json={
        "usuario_id": 1, "sala_id": 1, "data": data, "hora_inicio": "14:00", "hora_fim": "15:00"
    })
    assert r1.status_code == 201
    r2 = client.post("/reservas", json={
        "usuario_id": 1, "sala_id": 2, "data": data, "hora_inicio": "14:30", "hora_fim": "15:30"
    })
    assert r2.status_code == 400


def test_limite_2_reservas_ativas_dia():
    client.post("/usuarios", json={"nome": "Ana Souza", "email": "ana@email.com"})
    client.post("/salas", json={"nome": "Sala 101", "capacidade": 6, "bloco": "A"})
    client.post("/salas", json={"nome": "Sala 102", "capacidade": 6, "bloco": "A"})
    client.post("/salas", json={"nome": "Sala 103", "capacidade": 6, "bloco": "A"})
    data, _ = future_datetime(1, 8, 0)
    assert client.post("/reservas", json={"usuario_id": 1, "sala_id": 1, "data": data, "hora_inicio": "08:00", "hora_fim": "09:00"}).status_code == 201
    assert client.post("/reservas", json={"usuario_id": 1, "sala_id": 2, "data": data, "hora_inicio": "09:10", "hora_fim": "10:00"}).status_code == 201
    assert client.post("/reservas", json={"usuario_id": 1, "sala_id": 3, "data": data, "hora_inicio": "10:10", "hora_fim": "11:00"}).status_code == 400


def test_cancelar_reserva_ativa():
    client.post("/usuarios", json={"nome": "Ana Souza", "email": "ana@email.com"})
    client.post("/salas", json={"nome": "Sala 101", "capacidade": 6, "bloco": "A"})
    data, _ = future_datetime(1, 14, 0)
    r = client.post("/reservas", json={"usuario_id": 1, "sala_id": 1, "data": data, "hora_inicio": "14:00", "hora_fim": "15:00"})
    reserva_id = r.json()["id"]
    resp = client.put(f"/reservas/{reserva_id}/cancelar")
    assert resp.status_code == 200
    assert resp.json()["status"] == "canceled"


def test_finalizar_pos_fim():
    client.post("/usuarios", json={"nome": "Ana Souza", "email": "ana@email.com"})
    client.post("/salas", json={"nome": "Sala 101", "capacidade": 6, "bloco": "A"})
    data, _ = future_datetime(1, 8, 0)
    r = client.post("/reservas", json={"usuario_id": 1, "sala_id": 1, "data": data, "hora_inicio": "08:00", "hora_fim": "09:00"})
    reserva_id = r.json()["id"]
    resp = client.put(f"/reservas/{reserva_id}/finalizar?hora_atual=09:01")
    assert resp.status_code == 200
    assert resp.json()["status"] == "finished"


def test_finalizar_antes_do_fim():
    client.post("/usuarios", json={"nome": "Ana Souza", "email": "ana@email.com"})
    client.post("/salas", json={"nome": "Sala 101", "capacidade": 6, "bloco": "A"})
    data, _ = future_datetime(1, 8, 0)
    r = client.post("/reservas", json={"usuario_id": 1, "sala_id": 1, "data": data, "hora_inicio": "08:00", "hora_fim": "09:00"})
    reserva_id = r.json()["id"]
    resp = client.put(f"/reservas/{reserva_id}/finalizar?hora_atual=08:30")
    assert resp.status_code == 400
