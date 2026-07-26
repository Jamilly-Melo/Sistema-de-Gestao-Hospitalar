-- ETAPA 2 - ALTERAÇÕES ESTRUTURAIS

-- Este arquivo deve ser executado após:
-- 1. sql/criacao_tabela.sql
-- 2. sql/insercao_dados.sql


-- 1. UNIDADE EM QUE O ATENDIMENTO FOI REALIZADO
-- Necessária para calcular o tempo médio de espera por unidade e gerar estatísticas mensais por unidade.

ALTER TABLE atendimento
ADD COLUMN id_unidade INT;

ALTER TABLE atendimento
ADD CONSTRAINT fk_atendimento_unidade
FOREIGN KEY (id_unidade)
REFERENCES unidade(id_unidade)
ON UPDATE CASCADE
ON DELETE RESTRICT;

-- Adequação dos atendimentos inseridos na Etapa 1. As unidades existentes possuem IDs 1, 2 e 3.

UPDATE atendimento
SET id_unidade = CASE
    WHEN id_atendimento IN (1, 4, 7, 10) THEN 1
    WHEN id_atendimento IN (2, 5, 8) THEN 2
    WHEN id_atendimento IN (3, 6, 9) THEN 3
END;

-- Garante que todos os atendimentos estejam associados obrigatoriamente a uma unidade.

ALTER TABLE atendimento
ALTER COLUMN id_unidade SET NOT NULL;


-- 2. HORÁRIO DE INÍCIO DO PROCEDIMENTO REALIZADO
-- Necessário para calcular o tempo entre a chegada do paciente e o início do primeiro procedimento.

ALTER TABLE procedimento_realizado
ADD COLUMN data_hora_inicio TIMESTAMP;

-- Os registros antigos não possuíam horário de início. Para manter os dados válidos, foi definido um horário de teste 15 minutos após o início do atendimento.

UPDATE procedimento_realizado pr
SET data_hora_inicio = a.data_hora + INTERVAL '15 minutes'
FROM atendimento a
WHERE a.id_atendimento = pr.id_atendimento;

ALTER TABLE procedimento_realizado
ALTER COLUMN data_hora_inicio SET NOT NULL;


-- 3. MÉDIA REAL DO TEMPO DOS PROCEDIMENTOS
-- Essa coluna será atualizada automaticamente pela trigger trg_atualiza_media_procedimentos.

ALTER TABLE procedimento
ADD COLUMN media_tempo_procedimento NUMERIC(10, 2);

-- Inicializa a média usando os registros já existentes em procedimento_realizado.

UPDATE procedimento p
SET media_tempo_procedimento = media_procedimento.media_calculada
FROM (
    SELECT
        id_procedimento,
        ROUND(
            AVG(tempo_real_minutos)::NUMERIC,
            2
        ) AS media_calculada
    FROM procedimento_realizado
    GROUP BY id_procedimento
) AS media_procedimento
WHERE p.id_procedimento = media_procedimento.id_procedimento;


-- 4. TABELA DE AUDITORIA DOS ATENDIMENTOS
-- Será utilizada pela trigger trg_audita_atendimento para registrar operações de INSERT, UPDATE e DELETE.
-- id_atendimento não possui chave estrangeira porque o registro da auditoria deve continuar existindo mesmo depois da exclusão do atendimento original.

CREATE TABLE auditoria_atendimento (
    id_auditoria BIGSERIAL,
    id_atendimento INT,
    operacao VARCHAR(10) NOT NULL,
    usuario VARCHAR(100) NOT NULL,
    data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    dados_antigos JSONB,
    dados_novos JSONB,

    CONSTRAINT pk_auditoria_atendimento
        PRIMARY KEY (id_auditoria),

    CONSTRAINT ck_auditoria_atendimento_operacao
        CHECK (
            operacao IN ('INSERT', 'UPDATE', 'DELETE')
        )
);


-- 5. TABELA DE INTERNAÇÃO
-- Necessária para implementar a view vw_pacientes_internados. Uma internação permanece ativa enquanto data_hora_saida for NULL.
-- O paciente e a unidade podem ser obtidos por meio do atendimento relacionado, evitando repetição de dados.

CREATE TABLE internacao (
    id_internacao SERIAL,
    id_atendimento INT NOT NULL,
    data_hora_entrada TIMESTAMP NOT NULL,
    data_hora_saida TIMESTAMP,

    CONSTRAINT pk_internacao
        PRIMARY KEY (id_internacao),

    CONSTRAINT fk_internacao_atendimento
        FOREIGN KEY (id_atendimento)
        REFERENCES atendimento(id_atendimento)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_internacao_atendimento
        UNIQUE (id_atendimento),

    CONSTRAINT ck_internacao_datas
        CHECK (
            data_hora_saida IS NULL
            OR data_hora_saida >= data_hora_entrada
        )
);
