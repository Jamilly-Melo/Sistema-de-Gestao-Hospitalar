-- ETAPA 2 - STORED PROCEDURES

-- 1. REGISTRAR ATENDIMENTO COMPLETO
-- Recebe os dados do atendimento e uma lista JSONB de procedimentos realizados.
-- Caso qualquer inserção falhe, o CALL inteiro falha e a transação executada pela aplicação deve ser revertida.

CREATE OR REPLACE PROCEDURE sp_registrar_atendimento_completo(
    IN p_data_hora TIMESTAMP,
    IN p_duracao_minutos INT,
    IN p_id_paciente INT,
    IN p_id_residente INT,
    IN p_id_preceptor INT,
    IN p_id_unidade INT,
    IN p_procedimentos JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_atendimento INT;
    v_item JSONB;
    v_data_hora_inicio TIMESTAMP;
BEGIN
    -- Valida os dados básicos do atendimento.
    IF p_data_hora IS NULL
       OR p_duracao_minutos IS NULL
       OR p_id_paciente IS NULL
       OR p_id_residente IS NULL
       OR p_id_preceptor IS NULL
       OR p_id_unidade IS NULL
    THEN
        RAISE EXCEPTION
            'Todos os dados do atendimento devem ser informados.';
    END IF;

    IF p_duracao_minutos <= 0 THEN
        RAISE EXCEPTION
            'A duração do atendimento deve ser maior que zero.';
    END IF;

    -- O JSON precisa ser uma lista com pelo menos um procedimento.
    IF p_procedimentos IS NULL
       OR jsonb_typeof(p_procedimentos) <> 'array'
       OR jsonb_array_length(p_procedimentos) = 0
    THEN
        RAISE EXCEPTION
            'Deve ser informada uma lista JSON com pelo menos um procedimento.';
    END IF;

    INSERT INTO atendimento (
        data_hora,
        duracao_minutos,
        id_paciente,
        id_residente,
        id_preceptor,
        id_unidade
    )
    VALUES (
        p_data_hora,
        p_duracao_minutos,
        p_id_paciente,
        p_id_residente,
        p_id_preceptor,
        p_id_unidade
    )
    RETURNING id_atendimento
    INTO v_id_atendimento;

    FOR v_item IN
        SELECT value
        FROM jsonb_array_elements(p_procedimentos)
    LOOP
        -- Verifica os campos obrigatórios de cada item.
        IF NOT (
            v_item ? 'id_procedimento'
            AND v_item ? 'quantidade'
            AND v_item ? 'tempo_real_minutos'
            AND v_item ? 'data_hora_inicio'
        ) THEN
            RAISE EXCEPTION
                'Cada procedimento deve informar id_procedimento, quantidade, tempo_real_minutos e data_hora_inicio.';
        END IF;

        v_data_hora_inicio :=
            (v_item ->> 'data_hora_inicio')::TIMESTAMP;

        IF v_data_hora_inicio < p_data_hora THEN
            RAISE EXCEPTION
                'O procedimento não pode começar antes da chegada registrada no atendimento.';
        END IF;

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
            v_id_atendimento,
            (v_item ->> 'id_procedimento')::INT,
            (v_item ->> 'quantidade')::INT,
            (v_item ->> 'tempo_real_minutos')::INT,
            v_item ->> 'observacao',
            COALESCE(
                (v_item ->> 'faturado')::BOOLEAN,
                FALSE
            ),
            v_data_hora_inicio
        );
    END LOOP;

    RAISE NOTICE
        'Atendimento % registrado com sucesso.',
        v_id_atendimento;
END;
$$;


-- 2. CALCULAR TEMPO MÉDIO DE ESPERA
-- Uma procedure não retorna diretamente um conjunto de linhas no PostgreSQL. Por isso, utiliza um REFCURSOR.
-- A chamada deve ocorrer dentro de uma transação:
-- BEGIN;
-- CALL sp_calcular_tempo_medio_espera('resultado_espera');
-- FETCH ALL FROM resultado_espera;
-- COMMIT;

CREATE OR REPLACE PROCEDURE sp_calcular_tempo_medio_espera(
    INOUT p_resultado REFCURSOR
)
LANGUAGE plpgsql
AS $$
BEGIN
    OPEN p_resultado FOR
        WITH primeiro_procedimento AS (
            SELECT
                id_atendimento,
                MIN(data_hora_inicio) AS primeiro_inicio
            FROM procedimento_realizado
            GROUP BY id_atendimento
        )
        SELECT
            u.id_unidade,
            u.nome AS unidade,
            AVG(
                pp.primeiro_inicio - a.data_hora
            ) AS tempo_medio_espera
        FROM atendimento a
        JOIN unidade u
            ON u.id_unidade = a.id_unidade
        JOIN primeiro_procedimento pp
            ON pp.id_atendimento = a.id_atendimento
        GROUP BY
            u.id_unidade,
            u.nome
        ORDER BY
            u.nome;
END;
$$;


-- 3. REAJUSTAR ESCALA
-- Move as escalas de um residente de uma data e turno de origem para uma nova data e turno.
-- A operação é cancelada se o residente já possuir qualquer escala na data e turno de destino.

CREATE OR REPLACE PROCEDURE sp_reajustar_escala(
    IN p_id_residente INT,
    IN p_data_origem DATE,
    IN p_turno_origem VARCHAR(10),
    IN p_data_destino DATE,
    IN p_turno_destino VARCHAR(10)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_quantidade_origem INT;
BEGIN
    IF p_id_residente IS NULL
       OR p_data_origem IS NULL
       OR p_turno_origem IS NULL
       OR p_data_destino IS NULL
       OR p_turno_destino IS NULL
    THEN
        RAISE EXCEPTION
            'Todos os parâmetros da procedure devem ser informados.';
    END IF;

    IF p_turno_origem NOT IN ('MANHA', 'TARDE', 'NOITE')
       OR p_turno_destino NOT IN ('MANHA', 'TARDE', 'NOITE')
    THEN
        RAISE EXCEPTION
            'Turno inválido. Utilize MANHA, TARDE ou NOITE.';
    END IF;

    IF p_data_origem = p_data_destino
       AND p_turno_origem = p_turno_destino
    THEN
        RAISE EXCEPTION
            'A data e o turno de destino devem ser diferentes da origem.';
    END IF;

    -- Bloqueia os registros que serão reajustados.
    PERFORM 1
    FROM escala
    WHERE id_residente = p_id_residente
      AND data_plantao = p_data_origem
      AND turno = p_turno_origem
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'Nenhuma escala encontrada para o residente % em % no turno %.',
            p_id_residente,
            p_data_origem,
            p_turno_origem;
    END IF;

    SELECT COUNT(*)
    INTO v_quantidade_origem
    FROM escala
    WHERE id_residente = p_id_residente
      AND data_plantao = p_data_origem
      AND turno = p_turno_origem;

    -- Com a regra da Etapa 2, um residente não pode estar em
    -- duas unidades no mesmo dia e turno.
    IF v_quantidade_origem > 1 THEN
        RAISE EXCEPTION
            'O residente % possui mais de uma escala conflitante na origem. Corrija as escalas antes do reajuste.',
            p_id_residente;
    END IF;

    -- Impede conflito em qualquer unidade no destino.
    IF EXISTS (
        SELECT 1
        FROM escala
        WHERE id_residente = p_id_residente
          AND data_plantao = p_data_destino
          AND turno = p_turno_destino
    ) THEN
        RAISE EXCEPTION
            'O residente % já possui uma escala em % no turno %.',
            p_id_residente,
            p_data_destino,
            p_turno_destino;
    END IF;

    UPDATE escala
    SET
        data_plantao = p_data_destino,
        turno = p_turno_destino
    WHERE id_residente = p_id_residente
      AND data_plantao = p_data_origem
      AND turno = p_turno_origem;

    RAISE NOTICE
        'Escala do residente % reajustada de %/% para %/%.',
        p_id_residente,
        p_data_origem,
        p_turno_origem,
        p_data_destino,
        p_turno_destino;
END;
$$;
