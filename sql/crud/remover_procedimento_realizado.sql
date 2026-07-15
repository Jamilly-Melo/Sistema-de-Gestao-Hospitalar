-- Remover um procedimento realizado (apenas se ainda não houver faturamento associado)
-- Usa a flag faturado: só remove quando faturado = FALSE.
-- Params (ordem):
--   1) id_atendimento
--   2) id_procedimento

DELETE FROM procedimento_realizado
WHERE id_atendimento = %s
  AND id_procedimento = %s
  AND faturado = FALSE;
