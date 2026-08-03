"""Fixtures compartilhadas.

`executar_sql` usa exec_driver_sql, e não text(), porque os arquivos .sql do
projeto usam placeholders %s do psycopg2. O text() do SQLAlchemy espera :nome e
trataria os %s como texto literal.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.dependencies import get_session
from api.main import app
from sgh.database import SessionLocal, engine

ROOT = Path(__file__).resolve().parent.parent


def ordenado(linhas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordem canônica para comparar resultados de consultas SEM ORDER BY.

    Use com parcimônia: seis das sete consultas de leitura têm ORDER BY, e para
    essas a comparação deve ser na ordem retornada — a ordenação é parte do que
    o teste de paridade precisa verificar. Aplicar isto ali faria o teste aceitar
    uma direção trocada ou um ORDER BY removido sem reclamar.

    O caso legítimo é `media_atendimentos_por_residente`, a única consulta sem
    ORDER BY, onde a ordem das linhas é indefinida e comparar listas cruas daria
    falha intermitente sem bug nenhum.
    """
    return sorted(linhas, key=lambda linha: [str(valor) for valor in linha.values()])


@pytest.fixture
def executar_sql():
    def _executar(caminho: str, params: tuple = ()) -> list[dict[str, Any]]:
        sql = (ROOT / caminho).read_text(encoding="utf-8")
        with SessionLocal() as session:
            resultado = session.connection().exec_driver_sql(sql, params or None)
            return [dict(linha) for linha in resultado.mappings()]

    return _executar


@pytest.fixture
def session_revertida():
    """Sessão cujas escritas são desfeitas ao fim do teste.

    join_transaction_mode="create_savepoint" faz os commits internos das funções
    de escrita virarem savepoints dentro da transação externa, de modo que o
    rollback final desfaz tudo.
    """
    conexao = engine.connect()
    transacao = conexao.begin()
    session = Session(bind=conexao, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transacao.rollback()
        conexao.close()


@pytest.fixture
def cliente_api(session_revertida):
    """TestClient da API FastAPI, com `get_session` sobrescrito para usar a
    mesma sessão revertível dos testes de sgh/ (mesma transação/savepoint,
    desfeita ao fim do teste).

    Consolidado aqui a partir do helper `_cliente` que era duplicado em cada
    tests/test_api_*.py — cada um o chamava só com `next(...)`, então o
    teardown depois do `yield` nunca rodava.
    """

    def _get_session():
        yield session_revertida

    app.dependency_overrides[get_session] = _get_session
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
