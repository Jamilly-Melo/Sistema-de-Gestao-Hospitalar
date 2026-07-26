-- Sessão 1 do teste de concorrência (ver concorrencia.sql para o documento
-- completo e comentado).
-- Adquire o lock pessimista, insere a escala e segura a transação aberta por 10
-- segundos para dar tempo de a sessão 2 alcançar o mesmo SELECT ... FOR UPDATE e
-- bloquear.

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

SELECT pg_sleep(10);

COMMIT;
