-- ==========================================================
-- SISTEMA DE GESTÃO HOSPITALAR
-- ETAPA 2 - TESTE DE CONCORRÊNCIA
--
-- Objetivo:
-- Simular duas transações concorrentes tentando escalar
-- o mesmo residente para a mesma data, turno e unidade.
--
-- Estratégia:
-- Lock pessimista com SELECT ... FOR UPDATE.
--
-- IMPORTANTE:
-- Os blocos abaixo devem ser executados em duas sessões
-- separadas do PostgreSQL.
-- ==========================================================


-- ==========================================================
-- SESSÃO 1
-- ==========================================================

BEGIN;

SELECT id_profissional
FROM residente
WHERE id_profissional = 8
FOR UPDATE;

INSERT INTO escala (
    data_plantao,
    turno,
    id_unidade,
    id_residente,
    id_preceptor
)
VALUES (
    '2026-09-01',
    'MANHA',
    1,
    8,
    13
);

-- Manter esta transação aberta.
-- Depois que a Sessão 2 ficar bloqueada, executar:
--
-- COMMIT;


-- ==========================================================
-- SESSÃO 2
-- Executar em outro terminal enquanto a Sessão 1 está aberta.
-- ==========================================================

BEGIN;

SELECT id_profissional
FROM residente
WHERE id_profissional = 8
FOR UPDATE;

-- Este comando ficará aguardando até a Sessão 1 executar COMMIT.

INSERT INTO escala (
    data_plantao,
    turno,
    id_unidade,
    id_residente,
    id_preceptor
)
VALUES (
    '2026-09-01',
    'MANHA',
    1,
    8,
    13
);

-- A segunda inserção será impedida pela trigger
-- trg_check_sobreposicao_escala.

ROLLBACK;


-- ==========================================================
-- CONFERÊNCIA FINAL
-- ==========================================================

SELECT COUNT(*) AS quantidade_escalas
FROM escala
WHERE id_residente = 8
  AND data_plantao = '2026-09-01'
  AND turno = 'MANHA';

-- Resultado esperado:
-- quantidade_escalas = 1


-- ==========================================================
-- LIMPEZA DO DADO DE TESTE
-- ==========================================================

DELETE FROM escala
WHERE id_residente = 8
  AND data_plantao = '2026-09-01'
  AND turno = 'MANHA';