"""Mapeamento de exceções da camada de dados para respostas HTTP.

ValueError -> 422: regra de negócio recusada explicitamente em Python
(campo inválido, procedimento já faturado).
IntegrityError -> 409: violação de constraint do banco (corrida entre
checagem e escrita).
DBAPIError (genérico) -> 422: cobre o RAISE EXCEPTION das procedures da
etapa 2 (sp_reajustar_escala, sp_registrar_atendimento_completo), que chega
como InternalError/ProgrammingError — ambos são subclasses de DBAPIError.
A ordem de registro não importa: o FastAPI escolhe o handler mais específico
pela MRO da exceção, então IntegrityError nunca cai no handler genérico.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, IntegrityError


def registrar_handlers_de_erro(app: FastAPI) -> None:
    @app.exception_handler(ValueError)
    async def _handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(IntegrityError)
    async def _handle_integrity_error(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "detail": (
                    "Conflito de integridade: o registro referenciado pode "
                    "ter sido alterado por outra operação."
                )
            },
        )

    @app.exception_handler(DBAPIError)
    async def _handle_dbapi_error(request: Request, exc: DBAPIError) -> JSONResponse:
        diag = getattr(exc.orig, "diag", None)
        mensagem = getattr(diag, "message_primary", None) or str(exc.orig)
        return JSONResponse(status_code=422, content={"detail": mensagem})
