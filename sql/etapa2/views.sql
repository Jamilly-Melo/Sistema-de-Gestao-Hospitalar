-- ETAPA 2 - VIEWS

-- 1. PACIENTES ATUALMENTE INTERNADOS
-- Considera somente a internação mais recente de cada paciente e retorna aqueles cuja data_hora_saida é NULL.

CREATE OR REPLACE VIEW vw_pacientes_internados AS
WITH internacoes_ordenadas AS (
    SELECT
        i.id_internacao,
        i.id_atendimento,
        i.data_hora_entrada,
        i.data_hora_saida,
        a.id_paciente,
        a.id_unidade,
        ROW_NUMBER() OVER (
            PARTITION BY a.id_paciente
            ORDER BY i.data_hora_entrada DESC, i.id_internacao DESC
        ) AS ordem
    FROM internacao i
    JOIN atendimento a
        ON a.id_atendimento = i.id_atendimento
)
SELECT
    p.id_pessoa AS id_paciente,
    p.nome AS paciente,
    u.id_unidade,
    u.nome AS unidade,
    io.id_internacao,
    io.id_atendimento,
    io.data_hora_entrada,
    io.data_hora_saida
FROM internacoes_ordenadas io
JOIN pessoa p
    ON p.id_pessoa = io.id_paciente
JOIN unidade u
    ON u.id_unidade = io.id_unidade
WHERE io.ordem = 1
  AND io.data_hora_saida IS NULL;


-- 2. RESIDENTES SEM SUPERVISOR ADEQUADO
-- Exibe residentes escalados cujo preceptor não possui titulação de DOUTOR ou POS_DOUTOR.
-- Como a modelagem atual associa um preceptor diretamente a cada escala, não há registro de "supervisão ativa" separado. Assim, a view usa a titulação do preceptor vinculado ao plantão.

CREATE OR REPLACE VIEW vw_residentes_sem_supervisor AS
SELECT
    e.id_escala,
    e.data_plantao,
    e.turno,
    u.id_unidade,
    u.nome AS unidade,
    r.id_profissional AS id_residente,
    pr.nome AS residente,
    pc.id_profissional AS id_preceptor,
    pp.nome AS preceptor,
    pc.titulacao
FROM escala e
JOIN unidade u
    ON u.id_unidade = e.id_unidade
JOIN residente r
    ON r.id_profissional = e.id_residente
JOIN pessoa pr
    ON pr.id_pessoa = r.id_profissional
JOIN preceptor pc
    ON pc.id_profissional = e.id_preceptor
JOIN pessoa pp
    ON pp.id_pessoa = pc.id_profissional
WHERE pc.titulacao NOT IN ('DOUTOR', 'POS_DOUTOR');


-- 3. ESTATÍSTICAS MENSAIS DE ATENDIMENTOS
-- Exibe, por mês e por unidade:
-- - total de atendimentos;
-- - média de duração;
-- - procedimento mais comum;
-- - quantidade do procedimento mais comum.

CREATE OR REPLACE VIEW vw_estatisticas_atendimentos_mensal AS
WITH estatisticas_atendimento AS (
    SELECT
        DATE_TRUNC('month', a.data_hora)::DATE AS mes,
        a.id_unidade,
        COUNT(*) AS total_atendimentos,
        ROUND(
            AVG(a.duracao_minutos)::NUMERIC,
            2
        ) AS media_duracao_minutos
    FROM atendimento a
    GROUP BY
        DATE_TRUNC('month', a.data_hora)::DATE,
        a.id_unidade
),
quantidade_procedimentos AS (
    SELECT
        DATE_TRUNC('month', a.data_hora)::DATE AS mes,
        a.id_unidade,
        pr.id_procedimento,
        p.nome AS procedimento,
        SUM(pr.quantidade) AS quantidade_realizada
    FROM atendimento a
    JOIN procedimento_realizado pr
        ON pr.id_atendimento = a.id_atendimento
    JOIN procedimento p
        ON p.id_procedimento = pr.id_procedimento
    GROUP BY
        DATE_TRUNC('month', a.data_hora)::DATE,
        a.id_unidade,
        pr.id_procedimento,
        p.nome
),
ranking_procedimentos AS (
    SELECT
        qp.*,
        ROW_NUMBER() OVER (
            PARTITION BY qp.mes, qp.id_unidade
            ORDER BY
                qp.quantidade_realizada DESC,
                qp.procedimento ASC
        ) AS posicao
    FROM quantidade_procedimentos qp
)
SELECT
    ea.mes,
    u.id_unidade,
    u.nome AS unidade,
    ea.total_atendimentos,
    ea.media_duracao_minutos,
    rp.id_procedimento AS id_procedimento_mais_comum,
    rp.procedimento AS procedimento_mais_comum,
    rp.quantidade_realizada AS quantidade_procedimento_mais_comum
FROM estatisticas_atendimento ea
JOIN unidade u
    ON u.id_unidade = ea.id_unidade
LEFT JOIN ranking_procedimentos rp
    ON rp.mes = ea.mes
   AND rp.id_unidade = ea.id_unidade
   AND rp.posicao = 1;
