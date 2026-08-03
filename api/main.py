"""Ponto de entrada do FastAPI: cria o app e inclui os routers."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.errors import registrar_handlers_de_erro
from api.routers.atendimentos import router as atendimentos_router
from api.routers.escalas import router as escalas_router
from api.routers.lookups import router as lookups_router
from api.routers.pacientes import router as pacientes_router
from api.routers.profissionais import router as profissionais_router
from api.routers.relatorios import router as relatorios_router

app = FastAPI(title="Sistema de Gestão Hospitalar")
registrar_handlers_de_erro(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(atendimentos_router)
app.include_router(escalas_router)
app.include_router(lookups_router)
app.include_router(pacientes_router)
app.include_router(profissionais_router)
app.include_router(relatorios_router)
