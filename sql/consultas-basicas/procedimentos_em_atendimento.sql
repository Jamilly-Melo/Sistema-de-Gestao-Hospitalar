-- Listar os procedimentos realizados em um atendimento (com nome do procedimento, quantidade e tempo real)

SELECT 
    a.id_atendimento AS id_atendimento,
    a.data_hora AS data_hora,
    pro.nome AS nome,
    pro_re.quantidade AS quantidade,
    pro.tempo_medio_minutos,
    pro_re.tempo_real_minutos
FROM atendimento a
JOIN procedimento_realizado pro_re 
    ON a.id_atendimento = pro_re.id_atendimento
JOIN procedimento pro
    ON pro_re.id_procedimento = pro.id_procedimento
ORDER BY a.id_atendimento
