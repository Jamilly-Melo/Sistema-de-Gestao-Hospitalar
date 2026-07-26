-- ETAPA 2 - TESTES
-- Executar depois de:
-- 1. criacao_tabela.sql
-- 2. insercao_dados.sql
-- 3. alteracoes.sql
-- 4. procedures.sql
-- 5. triggers.sql
-- 6. views.sql

-- Este arquivo modifica os dados. Para repetir todos os
-- testes, recrie o banco antes de executá-lo novamente.


-- TESTE 1
-- sp_registrar_atendimento_completo

CALL sp_registrar_atendimento_completo(
    '2026-08-01 08:00:00',
    45,
    1,
    6,
    11,
    1,
    '[
        {
            "id_procedimento": 1,
            "quantidade": 1,
            "tempo_real_minutos": 12,
            "observacao": "Coleta realizada normalmente.",
            "faturado": false,
            "data_hora_inicio": "2026-08-01 08:10:00"
        },
        {
            "id_procedimento": 3,
            "quantidade": 1,
            "tempo_real_minutos": 15,
            "observacao": "Aplicação de medicação.",
            "faturado": false,
            "data_hora_inicio": "2026-08-01 08:25:00"
        }
    ]'::JSONB
);

-- Verifica o atendimento criado.

SELECT
    id_atendimento,
    data_hora,
    duracao_minutos,
    id_paciente,
    id_residente,
    id_preceptor,
    id_unidade
FROM atendimento
ORDER BY id_atendimento DESC
LIMIT 1;

-- Verifica os procedimentos do atendimento mais recente.

SELECT
    pr.id_atendimento,
    pr.id_procedimento,
    p.nome AS procedimento,
    pr.quantidade,
    pr.tempo_real_minutos,
    pr.data_hora_inicio,
    pr.faturado
FROM procedimento_realizado pr
JOIN procedimento p
    ON p.id_procedimento = pr.id_procedimento
WHERE pr.id_atendimento = (
    SELECT MAX(id_atendimento)
    FROM atendimento
)
ORDER BY pr.id_procedimento;


-- TESTE 2
-- Rollback da procedure quando um procedimento é inválido
-- O erro é capturado para que o restante do arquivo continue.
-- O atendimento não deve permanecer no banco.

DO $$
DECLARE
    v_total_antes INT;
    v_total_depois INT;
BEGIN
    SELECT COUNT(*)
    INTO v_total_antes
    FROM atendimento;

    BEGIN
        CALL sp_registrar_atendimento_completo(
            '2026-08-02 09:00:00',
            30,
            1,
            6,
            11,
            1,
            '[
                {
                    "id_procedimento": 999,
                    "quantidade": 1,
                    "tempo_real_minutos": 10,
                    "observacao": "Procedimento inexistente.",
                    "faturado": false,
                    "data_hora_inicio": "2026-08-02 09:10:00"
                }
            ]'::JSONB
        );

    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE
                'Erro esperado capturado: %',
                SQLERRM;
    END;

    SELECT COUNT(*)
    INTO v_total_depois
    FROM atendimento;

    IF v_total_antes <> v_total_depois THEN
        RAISE EXCEPTION
            'Falha no rollback: um atendimento inválido permaneceu no banco.';
    END IF;

    RAISE NOTICE
        'Rollback confirmado: nenhum atendimento inválido foi mantido.';
END;
$$;


-- TESTE 3
-- sp_reajustar_escala

CALL sp_reajustar_escala(
    6,
    '2026-07-05',
    'NOITE',
    '2026-07-15',
    'MANHA'
);


SELECT
    id_escala,
    data_plantao,
    turno,
    id_unidade,
    id_residente,
    id_preceptor
FROM escala
WHERE id_residente = 6
ORDER BY data_plantao, turno;


-- TESTE 4
-- sp_calcular_tempo_medio_espera
-- O REFCURSOR precisa ser utilizado dentro de uma transação.

BEGIN;

CALL sp_calcular_tempo_medio_espera(
    'resultado_tempo_espera'
);

FETCH ALL FROM resultado_tempo_espera;

COMMIT;


-- TESTE 5
-- trg_check_sobreposicao_escala
-- Tenta inserir o residente 6 no mesmo dia e turno em outra
-- unidade. A trigger deve impedir a inserção.

DO $$
BEGIN
    BEGIN
        INSERT INTO escala (
            data_plantao,
            turno,
            id_unidade,
            id_residente,
            id_preceptor
        )
        VALUES (
            '2026-07-15',
            'MANHA',
            2,
            6,
            12
        );

        RAISE EXCEPTION
            'Falha no teste: a escala conflitante foi aceita.';

    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM =
                'Falha no teste: a escala conflitante foi aceita.'
            THEN
                RAISE;
            END IF;

            RAISE NOTICE
                'Conflito de escala impedido corretamente: %',
                SQLERRM;
    END;
END;
$$;


-- Confirma que existe somente uma escala do residente nessa data e turno.

SELECT
    COUNT(*) AS quantidade_escalas
FROM escala
WHERE id_residente = 6
  AND data_plantao = '2026-07-15'
  AND turno = 'MANHA';


-- TESTE 6
-- trg_audita_atendimento

UPDATE atendimento
SET duracao_minutos = 50
WHERE id_atendimento = 1;


SELECT
    id_auditoria,
    id_atendimento,
    operacao,
    usuario,
    data_hora,
    dados_antigos,
    dados_novos
FROM auditoria_atendimento
ORDER BY id_auditoria;


-- TESTE 7
-- trg_atualiza_media_procedimentos
-- A combinação atendimento 1 + procedimento 1 já existe. Por isso, o teste utiliza o procedimento 2.

INSERT INTO procedimento_realizado (
    id_atendimento,
    id_procedimento,
    quantidade,
    tempo_real_minutos,
    observacao,
    faturado,
    data_hora_inicio
)
VALUES (
    1,
    2,
    1,
    18,
    'Teste da atualização automática da média.',
    FALSE,
    '2026-07-01 08:20:00'
);


SELECT
    id_procedimento,
    nome,
    media_tempo_procedimento
FROM procedimento
WHERE id_procedimento = 2;

-- O procedimento 2 possuía tempo real de 35 minutos.
-- Depois da inserção de 18 minutos, a média esperada é 26,50.


-- TESTE 8
-- Dados necessários para vw_pacientes_internados

INSERT INTO internacao (
    id_atendimento,
    data_hora_entrada,
    data_hora_saida
)
VALUES
    (
        1,
        '2026-07-01 09:00:00',
        '2026-07-03 14:00:00'
    ),
    (
        6,
        '2026-07-06 14:00:00',
        NULL
    );


-- TESTE 9
-- Views

SELECT *
FROM vw_pacientes_internados
ORDER BY paciente;


SELECT *
FROM vw_residentes_sem_supervisor
ORDER BY data_plantao, turno, residente;


SELECT *
FROM vw_estatisticas_atendimentos_mensal
ORDER BY mes, unidade;
