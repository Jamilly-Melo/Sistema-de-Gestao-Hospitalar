# Sistema de Gestão Hospitalar (SGH)

Projeto acadêmico de banco de dados que modela o domínio de um hospital universitário com residentes, preceptores, pacientes, atendimentos, procedimentos e escalas de plantão. Inclui scripts SQL (DDL, carga, consultas e CRUD), uma API FastAPI e um frontend Next.js para executar as queries de forma interativa.

## Objetivo

- Representar o modelo relacional do hospital com restrições de integridade (PK, FK, UNIQUE, CHECK).
- Disponibilizar consultas básicas, analíticas e operações CRUD parametrizadas para PostgreSQL.
- Facilitar a demonstração das queries via uma API HTTP (FastAPI) e um frontend web (Next.js) rodando em Docker.

## Stack

| Camada | Tecnologia |
|--------|------------|
| Banco | PostgreSQL 16 |
| API | FastAPI |
| Frontend | Next.js |
| Acesso aos dados | SQLAlchemy 2.0 (ORM), psycopg2 como driver |
| Empacotamento | uv + npm + Docker Compose |
| Linguagem | Python ≥ 3.12, TypeScript |

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
├── sgh/                    # Camada de dados — não importa streamlit nem pandas
│   ├── config.py           # DATABASE_URL a partir de variáveis de ambiente
│   ├── database.py         # engine, sessões e helpers de execução
│   ├── models/             # 14 models declarativos, por subdomínio
│   ├── queries/            # basicas.py, analiticas.py, crud.py
│   └── catalog.py          # catálogo de consultas consumido pela API
├── api/                    # API FastAPI — expõe sgh/ via HTTP (routers, schemas Pydantic)
├── web/                    # Frontend Next.js — consome a API FastAPI
├── tests/                  # paridade contra os .sql + testes funcionais do CRUD + testes de API
├── docker-compose.yaml     # database + db-init + api + web + profiles de teste
├── dockerfile              # imagem usada pelo serviço `testes` (roda pytest)
├── Dockerfile.api           # imagem do serviço `api`
├── pyproject.toml / uv.lock
├── documentacao/           # Modelagem conceitual e relacional (PDF)
└── sql/                    # DDL, carga, consultas e etapa 2 — fonte do schema
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
| `inserir_atendimento.sql` | INSERT com `EXISTS` para paciente/residente/preceptor/unidade | `data_hora`, `duracao_minutos`, `id_paciente`, `id_residente`, `id_preceptor`, `id_unidade` |
| `atualizar_dados_paciente.sql` | UPDATE de `endereco` ou `num_convenio` (via CTE) | `campo`, `valor`, `id_paciente` |
| `remover_procedimento_realizado.sql` | DELETE só se `faturado = FALSE` | `id_atendimento`, `id_procedimento` |

As queries CRUD usam placeholders `%s`.

Os arquivos `.sql` continuam sendo a fonte do schema (aplicados pelo `db-init`) e o
material da entrega. A aplicação não os executa mais: as consultas equivalentes
vivem em `sgh/queries/`, e os testes de paridade garantem que as duas versões
devolvem o mesmo resultado.

## API + Frontend

A `api/` expõe a camada `sgh/` via HTTP (FastAPI), e o `web/` é um frontend
Next.js que consome essa API.

- **API** — FastAPI na porta `8000`. Documentação OpenAPI interativa em
  [http://localhost:8000/docs](http://localhost:8000/docs).
- **Frontend** — Next.js na porta `3000`, com páginas para as consultas
  básicas/analíticas e as operações de CRUD.

Ambos sobem via `docker compose up -d --build`, nos serviços `api` e `web`.

### Configuração de conexão (API → banco)

A conexão vem de variáveis de ambiente, com os defaults do Compose:

| Variável | Default | Uso |
|---|---|---|
| `DB_HOST` | `database` | hostname do serviço no Compose |
| `DB_PORT` | `5432` | porta interna do container |
| `DB_NAME` | `sgh_db` | |
| `DB_USER` | `postgres` | |
| `DB_PASSWORD` | `postgres` | |

## Como executar

### Com Docker (recomendado)

```powershell
docker compose up -d --build
```

Serviços:

| Serviço | Função | Porta no host |
|---------|--------|---------------|
| `database` | PostgreSQL | `15435` → `5432` |
| `db-init` | Aplica etapa 1 (`criacao_tabela` + `insercao_dados`) e etapa 2 (`alteracoes`, `procedures`, `triggers`, `views`), com `ON_ERROR_STOP=1` | — (one-shot) |
| `api` | FastAPI | `8000` |
| `web` | Next.js | `3000` |

Acesse a interface em [http://localhost:3000](http://localhost:3000).

Cliente SQL externo (pgAdmin, DBeaver, `psql`) pode conectar em:

- Host: `localhost`
- Porta: `15435`
- DB / user / senha: `sgh_db` / `postgres` / `postgres`

### Localmente (sem Docker na API/frontend)

Útil para desenvolver a API ou a UI. O Postgres ainda precisa estar acessível
(Compose só com `database`, ou instância local).

```powershell
uv sync
```

Para rodar a API apontando para a porta publicada no host, sem editar código:

```powershell
$env:DB_HOST="localhost"; $env:DB_PORT="15435"; uv run uvicorn api.main:app --reload --port 8000
```

Para rodar o frontend, copie `web/.env.local.example` para `web/.env.local`
(ajustando a URL da API se necessário) e:

```powershell
cd web
npm run dev
```

## Testes

```powershell
docker compose --profile teste run --rm --build testes
```

Roda a suíte inteira contra um banco recém-criado: 7 testes de paridade, que
executam cada consulta ORM e o `.sql` que ela substitui e comparam os resultados,
e testes funcionais das 3 operações de escrita. No total são 48 testes (paridade
das consultas de leitura, funcionais das operações de escrita, models, conexão e
catálogo).

Localmente, com o banco do Compose no ar:

```powershell
$env:DB_HOST="localhost"; $env:DB_PORT="15435"; uv run pytest -v
```

### Demonstração de concorrência

```powershell
docker compose --profile concorrencia-sql up concorrencia-sessao-1 concorrencia-sessao-2
```

Sobe dois clientes `psql` simultâneos que tentam escalar o mesmo residente para a
mesma data, turno e unidade. A sessão 2 fica bloqueada no `SELECT ... FOR UPDATE`
até o `COMMIT` da sessão 1 e então é rejeitada pela trigger
`trg_check_sobreposicao_escala`.

É uma demonstração visual, não uma verificação automatizada — a coordenação entre
as sessões é por tempo. Concorrência não é coberta pela suíte de testes.

> **Lendo o log:** o `psql` faz buffering da saída quando não está num terminal
> interativo, então as linhas dos dois containers aparecem intercaladas de um
> jeito que pode sugerir que a sessão 2 não esperou. Ela esperou. Para conferir
> de verdade, compare a duração dos dois containers:
>
> ```powershell
> docker inspect --format '{{.Name}} {{.State.StartedAt}} {{.State.FinishedAt}}' `
>   sistema-de-gestao-hospitalar-concorrencia-sessao-2-1
> ```
>
> A sessão 2 leva cerca de 10 segundos e termina logo após o `COMMIT` da sessão 1
> — esse é o tempo em que ela ficou bloqueada no `SELECT ... FOR UPDATE`.

> **Repetindo a demonstração:** `docker compose down -v` não remove os
> containers dos profiles `teste` e `concorrencia-sql` — o Compose só age
> sobre profiles nomeados explicitamente. Se sobrar um container do
> `concorrencia-sql` de uma execução anterior apontando para uma rede que já
> foi removida, a próxima subida falha com
> `failed to set up container networking: network ... not found`. Isso é
> resíduo, não um problema da demonstração em si; limpe antes com:
>
> ```powershell
> docker compose --profile teste --profile concorrencia-sql down -v --remove-orphans
> ```
>
> Além disso, a sessão 1 faz `COMMIT` de uma escala real em `2026-09-01`. Numa
> segunda execução sem recriar o banco (só remover os containers não basta),
> essa mesma inserção já existe e a sessão 1 é rejeitada pela trigger — a
> demonstração passa a mostrar outra coisa. Para repetir de verdade, recrie o
> banco (`docker compose down -v` remove o volume `postgres_data`; `db-init`
> recarrega o schema na próxima subida).

## Principais considerações

1. **Host/porta dentro vs fora do container**  
   No Compose, a API fala com o Postgres pelo hostname `database` na porta **5432**. A porta **15435** é só o mapeamento no host (`15435:5432`).

   A porta publicada é **15435**, e não 5435, porque o Windows reserva
   dinamicamente a faixa 5358–5457 para o `winnat`; o bind na 5435 falha com
   "socket access forbidden". Verifique com
   `netsh int ipv4 show excludedportrange protocol=tcp`.

2. **`db-init` e volume persistente**  
   O volume `postgres_data` preserva os dados entre restarts. O serviço `db-init` executa os scripts SQL a cada subida (o DDL começa com `DROP TABLE ... CASCADE`). Se quiser um banco “limpo” do zero, remova o volume:
   ```powershell
   docker compose down -v
   docker compose up -d --build
   ```

3. **Parâmetros SQL**  
   Isto descreve os arquivos `.sql` em `sql/crud/` (fonte do schema e material da entrega), não a aplicação — que roda a versão equivalente em `sgh/queries/` via SQLAlchemy, sem `cursor.execute`. Nesses arquivos, placeholders são `%s` (psycopg2). Nomes de coluna **não** podem ser passados como `%s` com segurança; em `atualizar_dados_paciente.sql` o parâmetro `campo` escolhe entre valores permitidos (`endereco` | `num_convenio`) via CTE.

4. **Integridade no CRUD**  
   - Inserção de atendimento só ocorre se paciente, residente, preceptor e unidade existirem (`INSERT ... SELECT ... WHERE EXISTS`).  
   - Remoção de procedimento realizado exige `faturado = FALSE`.

5. **Dependências de build da imagem**  
   A imagem usa `python:3.12-slim` (Debian). Pacotes Ubuntu-only (ex.: `software-properties-common`) não devem ser instalados. São necessários `build-essential` e `libpq-dev` para o `psycopg2`.

6. **Documentação de modelagem**  
   PDFs de modelo conceitual, relacional e normalização estão em `documentacao/` e `documentacao/diagramas/`.

7. **Camadas**  
   `sgh/` não importa `streamlit` nem `pandas` — as funções devolvem
   `list[dict]`. Isso é o que permitiu servir a mesma camada de dados por
   HTTP (`api/`, FastAPI) para o frontend (`web/`, Next.js) sem reescrever nada.

8. **Limitações conhecidas**  
   A API e o frontend não têm autenticação nem autorização — qualquer
   cliente com acesso à rede pode ler e escrever todos os dados. É uma
   decisão de escopo deliberada para este projeto acadêmico, não um
   descuido: adicionar autenticação (ex.: JWT, sessão) fica fora do escopo
   atual.

## Credenciais padrão (desenvolvimento)

> Apenas para ambiente local/acadêmico — não usar em produção.

| Item | Valor |
|------|-------|
| Usuário | `postgres` |
| Senha | `postgres` |
| Database | `sgh_db` |
| Porta (host) | `15435` |
| Porta (rede Docker) | `5432` |
