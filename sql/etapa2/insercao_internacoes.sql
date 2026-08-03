-- ETAPA 2 - DADOS DE INTERNAÇÃO

-- Arquivo separado porque a tabela internacao nasce em alteracoes.sql, depois
-- de insercao_dados.sql já ter rodado. O seed da Etapa 1 não pode inserir numa
-- tabela que ainda não existe.

-- Todas as internações reaproveitam atendimentos do seed (ids 1 a 10):
-- alteracoes.sql faz `UPDATE atendimento SET id_unidade = CASE WHEN
-- id_atendimento IN (1,4,7,10)/(2,5,8)/(3,6,9)` seguido de SET NOT NULL, então
-- um atendimento com id fora dessas listas ficaria sem unidade e quebraria o
-- db-init inteiro.

-- NÃO usar os atendimentos 1 e 6 (paciente 1 / residente 6): três testes em
-- tests/test_paridade_leituras.py os apagam para montar o cenário "residente
-- sem atendimento", e a FK fk_internacao_atendimento é ON DELETE RESTRICT —
-- uma internação neles faz esses testes falharem por violação de chave.

-- vw_pacientes_internados não filtra apenas por data_hora_saida IS NULL: ela usa
-- ROW_NUMBER() PARTITION BY paciente ORDER BY data_hora_entrada DESC e considera
-- só a internação mais recente de cada um. Os dados abaixo exercitam essa regra,
-- não só o filtro de NULL — Bruno tem alta numa internação e está ativo em outra
-- mais recente, então precisa aparecer uma única vez, na unidade da mais nova.

INSERT INTO internacao (
    id_atendimento,
    data_hora_entrada,
    data_hora_saida
)
VALUES
    -- Diego, UTI: internado, sem alta.
    (4, '2026-07-04 12:00:00', NULL),

    -- Bruno, Enfermaria: alta depois de dois dias.
    (2, '2026-07-02 10:00:00', '2026-07-04 10:00:00'),

    -- Bruno de novo, agora na UTI e sem alta. Como esta entrada é mais recente
    -- que a anterior, é ela que a view considera: Bruno aparece na UTI.
    (7, '2026-07-07 15:00:00', NULL),

    -- Carla, Ambulatório: alta dada, não aparece na view.
    (3, '2026-07-03 11:00:00', '2026-07-05 11:00:00'),

    -- Eva, Enfermaria: internada, sem alta.
    (5, '2026-07-05 13:00:00', NULL);


-- Resultado esperado em vw_pacientes_internados: 3 linhas.
--   Bruno Soares Ferraz      — Unidade de Terapia Intensiva (reinternação)
--   Diego Justino Soares     — Unidade de Terapia Intensiva
--   Eva Pontes Vieira Pires  — Enfermaria Geral
-- Carla não aparece (recebeu alta) e Ana Silva não tem internação nenhuma.
