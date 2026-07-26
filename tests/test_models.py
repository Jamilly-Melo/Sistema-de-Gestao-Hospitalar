from sqlalchemy import select

from sgh.database import SessionLocal
from sgh.models import Paciente, Pessoa, Residente


def test_carrega_paciente_do_seed():
    with SessionLocal() as session:
        paciente = session.get(Paciente, 1)
        assert paciente is not None
        assert paciente.num_convenio == "C001"
        assert paciente.grupo_sanguineo == "A+"


def test_relacionamento_paciente_pessoa():
    with SessionLocal() as session:
        paciente = session.get(Paciente, 1)
        assert paciente.pessoa.nome == "Ana Silva dos Santos"
        assert paciente.pessoa.cpf == "11111111111"


def test_residente_chega_ate_pessoa_por_profissional():
    with SessionLocal() as session:
        residente = session.get(Residente, 6)
        assert residente.ano_residencia == "R1"
        assert residente.profissional.crm == "CRM001"
        assert residente.profissional.pessoa.nome == "Lucas Andrade Alves"


def test_conta_pessoas_do_seed():
    with SessionLocal() as session:
        assert len(session.execute(select(Pessoa.id_pessoa)).scalars().all()) == 15
