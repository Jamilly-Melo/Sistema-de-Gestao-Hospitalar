-- Atualizar um dado do paciente escolhendo a coluna por parâmetro.
-- Colunas permitidas: 'endereco' (pessoa) | 'num_convenio' (paciente)
--
-- Params (ordem):
--   1) campo  — 'endereco' ou 'num_convenio'
--   2) valor  — novo valor da coluna
--   3) id_paciente
--
-- Exemplo (psycopg2):
--   cursor.execute(sql, ('endereco', 'Rua Nova, 100', 1))
--   cursor.execute(sql, ('num_convenio', 'CONV-999', 1))
--   conn.commit()

WITH params AS (
    SELECT
        %s::text AS campo,
        %s::text AS valor,
        %s::int  AS id_paciente
),
upd_pessoa AS (
    UPDATE pessoa
    SET endereco = params.valor
    FROM params
    WHERE pessoa.id_pessoa = params.id_paciente
      AND params.campo = 'endereco'
      AND EXISTS (
          SELECT 1
          FROM paciente
          WHERE paciente.id_pessoa = pessoa.id_pessoa
      )
    RETURNING pessoa.id_pessoa
),
upd_paciente AS (
    UPDATE paciente
    SET num_convenio = params.valor
    FROM params
    WHERE paciente.id_pessoa = params.id_paciente
      AND params.campo = 'num_convenio'
    RETURNING paciente.id_pessoa
)
SELECT id_pessoa FROM upd_pessoa
UNION ALL
SELECT id_pessoa FROM upd_paciente;
