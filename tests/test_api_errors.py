"""Testa os exception handlers isoladamente, com rotas de teste dedicadas."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import DBAPIError, IntegrityError

from api.errors import registrar_handlers_de_erro


def _app_de_teste() -> FastAPI:
    app = FastAPI()
    registrar_handlers_de_erro(app)

    @app.get("/valor-invalido")
    def _valor_invalido():
        raise ValueError("campo inválido")

    @app.get("/conflito")
    def _conflito():
        raise IntegrityError("stmt", {}, Exception("fk violation"))

    @app.get("/erro-postgres")
    def _erro_postgres():
        class OrigFalso(Exception):
            diag = type("Diag", (), {"message_primary": "mensagem do postgres"})()

        raise DBAPIError("stmt", {}, OrigFalso("erro"))

    return app


def test_value_error_vira_422():
    cliente = TestClient(_app_de_teste(), raise_server_exceptions=False)
    resposta = cliente.get("/valor-invalido")
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "campo inválido"


def test_integrity_error_vira_409():
    cliente = TestClient(_app_de_teste(), raise_server_exceptions=False)
    resposta = cliente.get("/conflito")
    assert resposta.status_code == 409


def test_dbapi_error_vira_422_com_mensagem_do_postgres():
    cliente = TestClient(_app_de_teste(), raise_server_exceptions=False)
    resposta = cliente.get("/erro-postgres")
    assert resposta.status_code == 422
    assert resposta.json()["detail"] == "mensagem do postgres"
