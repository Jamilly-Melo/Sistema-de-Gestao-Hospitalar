"""Engine, fábrica de sessões e helpers de execução."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from sgh.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

# expire_on_commit=False para que atributos continuem legíveis depois do commit —
# as funções de escrita devolvem campos do objeto recém-inserido (ex.: o id gerado)
# e sem isso cada leitura dispararia um SELECT extra de refresh.
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def sessao(session: Session | None = None) -> Iterator[Session]:
    """Usa a sessão recebida ou cria uma própria.

    Receber a sessão de fora é o que torna as funções testáveis com rollback e,
    mais adiante, injetáveis por request num FastAPI. Quando a sessão vem de fora,
    quem a criou é responsável por fechá-la.
    """
    if session is not None:
        yield session
    else:
        with SessionLocal() as propria:
            yield propria


def fetch_all(stmt, session: Session | None = None) -> list[dict[str, Any]]:
    """Executa um select e devolve as linhas como dicionários."""
    with sessao(session) as s:
        return [dict(linha) for linha in s.execute(stmt).mappings()]
