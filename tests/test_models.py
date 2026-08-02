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
        # Seed: 15 pessoas originais + residente sem atendimento (16) +
        # paciente sem atendimento (17).
        assert len(session.execute(select(Pessoa.id_pessoa)).scalars().all()) == 17


def test_importa_as_quatorze_classes():
    import sgh.models as m

    esperadas = {
        "Pessoa", "Paciente", "PacienteAlergia", "Profissional", "Residente",
        "Preceptor", "Alergia", "Unidade", "Procedimento", "Atendimento",
        "ProcedimentoRealizado", "Internacao", "Escala", "AuditoriaAtendimento",
    }
    assert esperadas.issubset(set(dir(m)))


def test_relacionamento_atravessa_modulos():
    """Paciente (pessoas.py) -> Atendimento (atendimentos.py).

    Se o registry estiver incompleto, isto falha com InvalidRequestError ao
    resolver a string "Atendimento".
    """
    from sgh.models import Atendimento, Paciente

    with SessionLocal() as session:
        paciente = session.get(Paciente, 1)
        assert {a.id_atendimento for a in paciente.atendimentos} == {1, 6}


def test_atendimento_tem_coluna_da_etapa_2():
    from sgh.models import Atendimento

    with SessionLocal() as session:
        atendimento = session.get(Atendimento, 1)
        assert atendimento.id_unidade == 1


def test_procedimento_de_risco_alto():
    from sgh.models import Procedimento

    with SessionLocal() as session:
        assert session.get(Procedimento, 5).nivel_risco == "ALTO"
        assert session.get(Procedimento, 1).nivel_risco == "BAIXO"
