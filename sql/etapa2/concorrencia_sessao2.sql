-- Sessão 2 do teste de concorrência.
-- Espera 2 segundos para garantir que a sessão 1 já tenha adquirido o lock;
-- então tenta o mesmo SELECT ... FOR UPDATE, que fica bloqueado até o COMMIT da
-- sessão 1. Depois disso o INSERT é rejeitado pela trigger
-- trg_check_sobreposicao_escala.

SELECT pg_sleep(2);

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

COMMIT;
