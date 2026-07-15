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