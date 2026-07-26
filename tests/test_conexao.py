from sqlalchemy import text

from sgh.database import SessionLocal


def test_conecta_no_banco():
    with SessionLocal() as session:
        assert session.execute(text("SELECT 1")).scalar() == 1


def test_banco_tem_o_schema_da_etapa_2():
    """id_unidade só existe depois de alteracoes.sql."""
    with SessionLocal() as session:
        colunas = session.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'atendimento'"
            )
        ).scalars().all()
    assert "id_unidade" in colunas
