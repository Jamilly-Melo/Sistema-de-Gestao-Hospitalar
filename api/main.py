"""Ponto de entrada do FastAPI: cria o app e inclui os routers."""

from __future__ import annotations

from fastapi import FastAPI

from api.errors import registrar_handlers_de_erro

app = FastAPI(title="Sistema de Gestão Hospitalar")
registrar_handlers_de_erro(app)
