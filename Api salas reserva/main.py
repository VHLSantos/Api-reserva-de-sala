from fastapi import FastAPI
from api.routes.usuarios import router as usuarios_router
from api.routes.salas import router as salas_router
from api.routes.reservas import router as reservas_router

app = FastAPI(title="API de Reserva de Salas de Estudo")

app.include_router(usuarios_router)
app.include_router(salas_router)
app.include_router(reservas_router)


@app.get("/")
def home():
    return {"message": "API online"}
