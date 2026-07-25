-- ==========================================================
-- SISTEMA DE GESTÃO HOSPITALAR
-- ETAPA 2 - TRIGGERS
-- ==========================================================

-- ==========================================================
-- 1. IMPEDIR SOBREPOSIÇÃO DE ESCALAS
-- ==========================================================

CREATE OR REPLACE FUNCTION fn_check_sobreposicao_escala()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN

    IF EXISTS (
        SELECT 1
        FROM escala
        WHERE id_residente = NEW.id_residente
          AND data_plantao = NEW.data_plantao
          AND turno = NEW.turno
          AND id_escala <> COALESCE(NEW.id_escala,0)
    ) THEN

        RAISE EXCEPTION
        'O residente já possui uma escala neste dia e turno.';

    END IF;

    RETURN NEW;

END;
$$;


CREATE TRIGGER trg_check_sobreposicao_escala
BEFORE INSERT OR UPDATE
ON escala
FOR EACH ROW
EXECUTE FUNCTION fn_check_sobreposicao_escala();




-- ==========================================================
-- 2. AUDITORIA DE ATENDIMENTOS
-- ==========================================================

CREATE OR REPLACE FUNCTION fn_audita_atendimento()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN

    IF TG_OP = 'INSERT' THEN

        INSERT INTO auditoria_atendimento(
            id_atendimento,
            operacao,
            usuario,
            dados_antigos,
            dados_novos
        )
        VALUES(
            NEW.id_atendimento,
            TG_OP,
            CURRENT_USER,
            NULL,
            to_jsonb(NEW)
        );

        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN

        INSERT INTO auditoria_atendimento(
            id_atendimento,
            operacao,
            usuario,
            dados_antigos,
            dados_novos
        )
        VALUES(
            NEW.id_atendimento,
            TG_OP,
            CURRENT_USER,
            to_jsonb(OLD),
            to_jsonb(NEW)
        );

        RETURN NEW;

    ELSE

        INSERT INTO auditoria_atendimento(
            id_atendimento,
            operacao,
            usuario,
            dados_antigos,
            dados_novos
        )
        VALUES(
            OLD.id_atendimento,
            TG_OP,
            CURRENT_USER,
            to_jsonb(OLD),
            NULL
        );

        RETURN OLD;

    END IF;

END;
$$;


CREATE TRIGGER trg_audita_atendimento
AFTER INSERT OR UPDATE OR DELETE
ON atendimento
FOR EACH ROW
EXECUTE FUNCTION fn_audita_atendimento();




-- ==========================================================
-- 3. ATUALIZA MÉDIA DOS PROCEDIMENTOS
-- ==========================================================

CREATE OR REPLACE FUNCTION fn_atualiza_media_procedimentos()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN

    UPDATE procedimento
    SET media_tempo_procedimento = (

        SELECT ROUND(
            AVG(tempo_real_minutos)::NUMERIC,
            2
        )

        FROM procedimento_realizado

        WHERE id_procedimento = NEW.id_procedimento

    )

    WHERE id_procedimento = NEW.id_procedimento;

    RETURN NEW;

END;
$$;


CREATE TRIGGER trg_atualiza_media_procedimentos
AFTER INSERT
ON procedimento_realizado
FOR EACH ROW
EXECUTE FUNCTION fn_atualiza_media_procedimentos();