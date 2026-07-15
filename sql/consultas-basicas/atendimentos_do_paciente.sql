-- Listar todos os atendimentos de um paciente específico (ordenados por data)

SELECT pessoa.nome, atendimento.data_hora FROM paciente
JOIN pessoa ON paciente.id_pessoa = pessoa.id_pessoa
LEFT JOIN atendimento ON paciente.id_pessoa = atendimento.id_paciente
ORDER BY atendimento.data_hora DESC;