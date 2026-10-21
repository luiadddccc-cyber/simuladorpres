from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.routes.auth import router as auth_router
from backend.routes.simulation import router as sim_router
from backend.database.connection import init_db

app = FastAPI(title="Simulador Presidencial")
init_db()

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(sim_router, prefix="/api/sim", tags=["Simulation"])

frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))
