-- Calcular o tempo médio de duração dos atendimentos por residente

SELECT
    r.id_profissional AS id,
    pe.nome AS nome,
    r.ano_residencia AS ano_residencia,
    pr.crm AS CRM,
    AVG(a.duracao_minutos) AS tempo_medio_de_atendimentos
FROM residente r
JOIN profissional pr
    ON r.id_profissional = pr.id_pessoa
JOIN pessoa pe
    ON pr.id_pessoa = pe.id_pessoa
JOIN atendimento a
    ON pe.id_pessoa = a.id_residente
GROUP BY id, nome, CRM, ano_residencia;
