"""Dependências compartilhadas pelos routers."""

from __future__ import annotations

from typing import Iterator

from sqlalchemy.orm import Session

from sgh.database import SessionLocal


def get_session() -> Iterator[Session]:
    """Uma sessão por request, fechada ao fim — o Depends do FastAPI."""
    with SessionLocal() as session:
        yield session
