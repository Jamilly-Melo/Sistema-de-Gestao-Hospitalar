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