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