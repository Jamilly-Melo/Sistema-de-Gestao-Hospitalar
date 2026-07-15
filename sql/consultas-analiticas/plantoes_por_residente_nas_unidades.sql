--Para cada unidade, mostra a quantidade de plantões escalados por residente no mês corrente
--Inclui residentes sem plantão (unidade NULL e total_plantoes = 0)

SELECT
    u.nome AS unidade,
    pe.nome AS residente,
    COUNT(e.id_escala) AS total_plantoes
FROM residente r
JOIN profissional pr
    ON pr.id_pessoa = r.id_profissional
JOIN pessoa pe
    ON pe.id_pessoa = pr.id_pessoa
LEFT JOIN escala e
    ON e.id_residente = r.id_profissional
   AND e.data_plantao >= DATE_TRUNC('month', CURRENT_DATE)
   AND e.data_plantao <  DATE_TRUNC('month', CURRENT_DATE)
                          + INTERVAL '1 month'
LEFT JOIN unidade u
    ON u.id_unidade = e.id_unidade
GROUP BY
    u.id_unidade,
    u.nome,
    r.id_profissional,
    pe.nome
ORDER BY
    u.nome ASC NULLS LAST,
    total_plantoes DESC,
    pe.nome ASC;
