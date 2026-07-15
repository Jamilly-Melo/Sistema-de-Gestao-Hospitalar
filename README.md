# Sistema de Gestão Hospitalar (SGH)

Projeto acadêmico de banco de dados que modela o domínio de um hospital universitário com residentes, preceptores, pacientes, atendimentos, procedimentos e escalas de plantão. Inclui scripts SQL (DDL, carga, consultas e CRUD) e uma interface Streamlit para executar as queries de forma interativa.

## Objetivo

- Representar o modelo relacional do hospital com restrições de integridade (PK, FK, UNIQUE, CHECK).
- Disponibilizar consultas básicas, analíticas e operações CRUD parametrizadas para PostgreSQL.
- Facilitar a demonstração das queries via interface web (Streamlit) rodando em Docker.

## Stack

| Camada | Tecnologia |
|--------|------------|
| Banco | PostgreSQL 16 |
| Interface | Streamlit + pandas |
| Acesso aos dados | psycopg2 |
| Empacotamento | uv + Docker Compose |
| Linguagem | Python ≥ 3.12 |

## Domínio (resumo)

O modelo gira em torno de `pessoa` (dados cadastrais) e especializações:

- **Paciente** — convênio, grupo sanguíneo, alergias.
- **Profissional** — CRM, especialidade; subdividido em **residente** e **preceptor**.
- **Atendimento** — paciente + residente + preceptor, com duração e data/hora.
- **Procedimento / procedimento_realizado** — catálogo e execução no atendimento (com flag `faturado`).
- **Unidade / escala** — plantões de residentes supervisionados por preceptores.

Diagramas e material de modelagem estão em `documentacao/`.

### Tabelas

`pessoa`, `paciente`, `alergia`, `paciente_alergia`, `profissional`, `residente`, `preceptor`, `unidade`, `procedimento`, `atendimento`, `procedimento_realizado`, `escala`

## Estrutura do repositório

```text
.
├── main.py                 # Interface Streamlit
├── docker-compose.yaml     # database + db-init + frontend
├── dockerfile              # Imagem do frontend Streamlit
├── pyproject.toml / uv.lock
├── documentacao/           # Modelagem conceitual e relacional (PDF)
└── sql/
    ├── criacao_tabela.sql          # DDL (DROP + CREATE + constraints)
    ├── insercao_dados.sql          # Carga inicial
    ├── consultas-basicas/          # Consultas simples
    ├── consultas-analiticas/       # Agregações / análises
    └── crud/                       # INSERT / UPDATE / DELETE parametrizados
```

## Queries SQL

### Consultas básicas (`sql/consultas-basicas/`)

| Arquivo | Descrição |
|---------|-----------|
| `atendimentos_do_paciente.sql` | Atendimentos ordenados por data |
| `media_atendimentos_por_residente.sql` | Tempo médio de duração por residente |
| `procedimentos_em_atendimento.sql` | Procedimentos realizados em cada atendimento |

### Consultas analíticas (`sql/consultas-analiticas/`)

| Arquivo | Descrição |
|---------|-----------|
| `ranking_residentes.sql` | Ranking por número de atendimentos |
| `plantoes_por_residente_nas_unidades.sql` | Plantões no mês corrente por unidade |
| `pacientes_sem_procedimento_risco_alto.sql` | Pacientes sem procedimento de risco ALTO |
| `preceptores_que_supervisionaram.sql` | Preceptores com > 5 atendimentos em um intervalo (**parametrizada**) |

### CRUD (`sql/crud/`)

| Arquivo | Operação | Parâmetros (`%s`) |
|---------|----------|-------------------|
| `inserir_atendimento.sql` | INSERT com `EXISTS` para paciente/residente/preceptor | `data_hora`, `duracao_minutos`, `id_paciente`, `id_residente`, `id_preceptor` |
| `atualizar_dados_paciente.sql` | UPDATE de `endereco` ou `num_convenio` (via CTE) | `campo`, `valor`, `id_paciente` |
| `remover_procedimento_realizado.sql` | DELETE só se `faturado = FALSE` | `id_atendimento`, `id_procedimento` |

As queries CRUD usam placeholders `%s` compatíveis com `psycopg2` (`cursor.execute(sql, params)`).

## Interface Streamlit

O `main.py` organiza as queries por categoria na sidebar:

1. Escolha a **categoria** (básicas / analíticas / CRUD).
2. Escolha a **query**.
3. Preencha os **parâmetros** (quando houver).
4. Clique em **Executar** — resultados em tabela; operações de escrita fazem `commit`.

Conexão fixa (ambiente Docker):

```python
host = "database"   # nome do serviço no Compose
port = "5432"       # porta interna do container Postgres
database = "sgh_db"
user = "postgres"
password = "postgres"
```

## Como executar

### Com Docker (recomendado)

```powershell
docker compose up -d --build
```

Serviços:

| Serviço | Função | Porta no host |
|---------|--------|---------------|
| `database` | PostgreSQL | `5435` → `5432` |
| `db-init` | Aplica `criacao_tabela.sql` + `insercao_dados.sql` | — (one-shot) |
| `frontend` | Streamlit | `8501` |

Acesse a interface em [http://localhost:8501](http://localhost:8501).

Cliente SQL externo (pgAdmin, DBeaver, `psql`) pode conectar em:

- Host: `localhost`
- Porta: `5435`
- DB / user / senha: `sgh_db` / `postgres` / `postgres`

### Localmente (sem Docker no frontend)

Útil para desenvolver a UI. O Postgres ainda precisa estar acessível (Compose só com `database`, ou instância local).

Nesse caso, altere temporariamente o `DB_CONFIG` no `main.py` para `host="localhost"` e `port="5435"`, depois:

```powershell
uv sync
uv run streamlit run main.py
```

## Principais considerações

1. **Host/porta dentro vs fora do container**  
   No Compose, o frontend fala com o Postgres pelo hostname `database` na porta **5432**. A porta **5435** é só o mapeamento no host (`5435:5432`).

2. **`db-init` e volume persistente**  
   O volume `postgres_data` preserva os dados entre restarts. O serviço `db-init` executa os scripts SQL a cada subida (o DDL começa com `DROP TABLE ... CASCADE`). Se quiser um banco “limpo” do zero, remova o volume:
   ```powershell
   docker compose down -v
   docker compose up -d --build
   ```

3. **Parâmetros SQL**  
   Placeholders são `%s` (psycopg2). Nomes de coluna **não** podem ser passados como `%s` com segurança; em `atualizar_dados_paciente.sql` o parâmetro `campo` escolhe entre valores permitidos (`endereco` | `num_convenio`) via CTE.

4. **Integridade no CRUD**  
   - Inserção de atendimento só ocorre se paciente, residente e preceptor existirem (`INSERT ... SELECT ... WHERE EXISTS`).  
   - Remoção de procedimento realizado exige `faturado = FALSE`.

5. **Dependências de build da imagem**  
   A imagem usa `python:3.12-slim` (Debian). Pacotes Ubuntu-only (ex.: `software-properties-common`) não devem ser instalados. São necessários `build-essential` e `libpq-dev` para o `psycopg2`.

6. **Documentação de modelagem**  
   PDFs de modelo conceitual, relacional e normalização estão em `documentacao/` e `documentacao/diagramas/`.

## Credenciais padrão (desenvolvimento)

> Apenas para ambiente local/acadêmico — não usar em produção.

| Item | Valor |
|------|-------|
| Usuário | `postgres` |
| Senha | `postgres` |
| Database | `sgh_db` |
| Porta (host) | `5435` |
| Porta (rede Docker) | `5432` |
