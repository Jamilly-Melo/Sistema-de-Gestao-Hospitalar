--Ranking dos residentes por número de atendimentos realizados 

SELECT
    pe.nome AS residente,
    COUNT(a.id_atendimento) AS total_atendimentos
FROM residente r
JOIN profissional pr
    ON pr.id_pessoa = r.id_profissional
JOIN pessoa pe
    ON pe.id_pessoa = pr.id_pessoa
LEFT JOIN atendimento a
    ON a.id_residente = r.id_profissional
GROUP BY
    r.id_profissional,
    pe.nome
ORDER BY
    total_atendimentos DESC,
    pe.nome ASC;

--Lista os preceptores que supervisionaram mais de 5 atendimentos em um determinado mês

SELECT
    pe.nome AS preceptor,
    COUNT(a.id_atendimento) AS total_atendimentos
FROM preceptor p
JOIN profissional pr
    ON pr.id_pessoa = p.id_profissional
JOIN pessoa pe
    ON pe.id_pessoa = pr.id_pessoa
JOIN atendimento a
    ON a.id_preceptor = p.id_profissional
WHERE a.data_hora >= TIMESTAMP '2026-07-01 00:00:00'
  AND a.data_hora <  TIMESTAMP '2026-08-01 00:00:00'
GROUP BY
    p.id_profissional,
    pe.nome
HAVING COUNT(a.id_atendimento) > 5
ORDER BY
    total_atendimentos DESC,
    pe.nome ASC;

--Para cada unidade, mostra a quantidade de plantões escalados por residente no mês corrente

SELECT
    u.nome AS unidade,
    pe.nome AS residente,
    COUNT(e.id_escala) AS total_plantoes
FROM escala e
JOIN unidade u
    ON u.id_unidade = e.id_unidade
JOIN residente r
    ON r.id_profissional = e.id_residente
JOIN profissional pr
    ON pr.id_pessoa = r.id_profissional
JOIN pessoa pe
    ON pe.id_pessoa = pr.id_pessoa
WHERE e.data_plantao >= DATE_TRUNC('month', CURRENT_DATE)
  AND e.data_plantao < DATE_TRUNC('month', CURRENT_DATE)
                         + INTERVAL '1 month'
GROUP BY
    u.id_unidade,
    u.nome,
    r.id_profissional,
    pe.nome
ORDER BY
    u.nome ASC,
    total_plantoes DESC,
    pe.nome ASC;

--Lista pacientes que nunca realizaram nenhum procedimento de nível de risco ALTO.
SELECT
    pe.id_pessoa,
    pe.nome AS paciente
FROM paciente pa
JOIN pessoa pe
    ON pe.id_pessoa = pa.id_pessoa
WHERE NOT EXISTS (
    SELECT 1
    FROM atendimento a
    JOIN procedimento_realizado pr
        ON pr.id_atendimento = a.id_atendimento
    JOIN procedimento p
        ON p.id_procedimento = pr.id_procedimento
    WHERE a.id_paciente = pa.id_pessoa
      AND p.nivel_risco = 'ALTO'
)
ORDER BY
    pe.nome ASC;