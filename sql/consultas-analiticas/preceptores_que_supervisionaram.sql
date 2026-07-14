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
WHERE a.data_hora >= TIMESTAMP %s
  AND a.data_hora <  TIMESTAMP %s
GROUP BY
    p.id_profissional,
    pe.nome
HAVING COUNT(a.id_atendimento) > 5
ORDER BY
    total_atendimentos DESC,
    pe.nome ASC;