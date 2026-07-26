-- Inserir um novo atendimento (verificando se paciente, residente, preceptor e
-- unidade existem)
-- Só insere se os quatro IDs existirem nas respectivas tabelas.
-- Params (ordem):
--   1) data_hora
--   2) duracao_minutos
--   3) id_paciente
--   4) id_residente
--   5) id_preceptor
--   6) id_unidade

INSERT INTO atendimento (
    data_hora,
    duracao_minutos,
    id_paciente,
    id_residente,
    id_preceptor,
    id_unidade
)
SELECT
    v.data_hora,
    v.duracao_minutos,
    v.id_paciente,
    v.id_residente,
    v.id_preceptor,
    v.id_unidade
FROM (
    VALUES (%s::timestamp, %s::int, %s::int, %s::int, %s::int, %s::int)
) AS v(
    data_hora,
    duracao_minutos,
    id_paciente,
    id_residente,
    id_preceptor,
    id_unidade
)
WHERE EXISTS (
    SELECT 1 FROM paciente WHERE id_pessoa = v.id_paciente
)
AND EXISTS (
    SELECT 1 FROM residente WHERE id_profissional = v.id_residente
)
AND EXISTS (
    SELECT 1 FROM preceptor WHERE id_profissional = v.id_preceptor
)
AND EXISTS (
    SELECT 1 FROM unidade WHERE id_unidade = v.id_unidade
)
RETURNING
    id_atendimento,
    data_hora,
    duracao_minutos,
    id_paciente,
    id_residente,
    id_preceptor,
    id_unidade;
