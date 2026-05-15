# API de Reserva de Salas de Estudo

## Como executar

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoints

- POST /usuarios
- GET /usuarios
- POST /salas
- GET /salas
- POST /reservas
- GET /reservas
- GET /reservas/{reserva_id}
- GET /reservas/usuario/{usuario_id}
- PUT /reservas/{reserva_id}/cancelar
- PUT /reservas/{reserva_id}/finalizar

## Testes

```bash
pytest
```
