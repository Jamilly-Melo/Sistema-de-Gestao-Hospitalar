-- Inserir um novo atendimento (verificando se paciente, residente e preceptor existem)
-- Só insere se os três IDs existirem nas respectivas tabelas.
-- Params (ordem):
--   1) data_hora
--   2) duracao_minutos
--   3) id_paciente
--   4) id_residente
--   5) id_preceptor

INSERT INTO atendimento (
    data_hora,
    duracao_minutos,
    id_paciente,
    id_residente,
    id_preceptor
)
SELECT
    v.data_hora,
    v.duracao_minutos,
    v.id_paciente,
    v.id_residente,
    v.id_preceptor
FROM (
    VALUES (%s::timestamp, %s::int, %s::int, %s::int, %s::int)
) AS v(data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor)
WHERE EXISTS (
    SELECT 1 FROM paciente WHERE id_pessoa = v.id_paciente
)
AND EXISTS (
    SELECT 1 FROM residente WHERE id_profissional = v.id_residente
)
AND EXISTS (
    SELECT 1 FROM preceptor WHERE id_profissional = v.id_preceptor
)
RETURNING
    id_atendimento,
    data_hora,
    duracao_minutos,
    id_paciente,
    id_residente,
    id_preceptor;
