# pipeline-medalion-ml-enterprise-cicd

Plataforma de dados em arquitetura Medallion estendida para ML, com:

- Bronze / Silver / Gold Core / Gold ML
- Versionamento multi‑modelo de ML (configuração declarativa em JSON)
- Registry Delta para rastreio de versões de modelos
- Orquestração via Databricks Job (`orchestration/job_entrypoint.py`)
- Testes automatizados com `pytest`
- Pipeline de CI/CD multi‑ambiente com GitHub Actions

Para detalhes aprofundados, veja também:

- `SYSTEM_ARCHITECTURE.md` – visão técnica e fluxo da arquitetura
- `DATA_CONTRACTS_AND_RULES.md` – contratos formais de dados e regras por camada

---

### Estrutura de pastas (principal)

```text
.
├── src
│   ├── bronze
│   │   └── bronze_ingestion.py        # ingestão bruta → bronze.sales_raw
│   ├── silver
│   │   └── silver_transformation.py   # limpeza → silver.sales_clean
│   ├── gold_core
│   │   └── gold_core_builder.py       # métricas de negócio → gold_core.customer_metrics
│   ├── ml
│   │   └── gold_ml_generator.py       # datasets por modelo → gold_ml.<model>_v<version>
│   └── registry
│       └── model_registry.py          # registry → ml_registry.model_versions
│
├── orchestration
│   └── job_entrypoint.py              # orquestra o pipeline end‑to‑end
│
├── config
│   └── ml_models.json                 # definição declarativa dos modelos de ML
│
├── tests
│   └── test_config.py                 # validação da configuração dos modelos
│
├── .github
│   └── workflows
│       └── ci-cd.yml                  # pipeline de CI/CD multi‑ambiente
│
├── SYSTEM_ARCHITECTURE.md
├── DATA_CONTRACTS_AND_RULES.md
├── requirements.txt
└── README.md
```

---

### Quickstart – desenvolvimento local

#### 1. Pré‑requisitos

- Python 3.10+
- Acesso a um cluster Spark (Databricks ou Spark local configurado com Delta) para execução fim a fim.

#### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

#### 3. Rodar testes unitários

```bash
pytest
```

O arquivo `tests/test_config.py` garante que `config/ml_models.json`:

- Possui a chave `models`
- Lista apenas modelos bem definidos
- Valida campos obrigatórios (nome, versão, tabela de origem, features, target)

---

### Execução do pipeline localmente

O entrypoint do pipeline é `orchestration/job_entrypoint.py`, que expõe a função `run_pipeline` e executa as etapas:

1. Bronze: `ingest_raw("sales_raw", RAW_SALES_PATH)`
2. Silver: `transform_sales()`
3. Gold Core: `build_customer_metrics()`
4. Gold ML: `generate_models(PIPELINE_CONFIG_PATH)`

Variáveis de ambiente suportadas:

- `RAW_SALES_PATH`: caminho do CSV de vendas bruto  
  - Default: `/mnt/raw/sales.csv` (montagem típica em Databricks)
- `PIPELINE_CONFIG_PATH`: caminho para o arquivo de configuração dos modelos  
  - Default: `config/ml_models.json`

Exemplo (Linux/macOS):

```bash
export RAW_SALES_PATH="/caminho/para/sales.csv"
export PIPELINE_CONFIG_PATH="config/ml_models.json"
python orchestration/job_entrypoint.py
```

Exemplo (PowerShell no Windows):

```powershell
$env:RAW_SALES_PATH="C:\caminho\para\sales.csv"
$env:PIPELINE_CONFIG_PATH="config/ml_models.json"
python orchestration/job_entrypoint.py
```

> Observação: para executar integralmente as operações Delta Lake fora do Databricks,
> é necessário ter um ambiente Spark com suporte a Delta configurado (por exemplo,
> adicionando `delta-spark` e configurando o `SparkSession` apropriadamente).

---

### CI/CD – fluxo multi‑ambiente

O workflow GitHub Actions está em `.github/workflows/ci-cd.yml` e executa:

1. `build-test` (sempre que houver `push`/`pull_request` para `main`):
   - Instala dependências
   - Executa `pytest`
2. `deploy-dev` (após sucesso em `build-test`):
   - Deploy para `/Shared/pipeline-medalion-dev`
3. `deploy-staging` (após sucesso em `deploy-dev`):
   - Deploy para `/Shared/pipeline-medalion-staging`
4. `deploy-prod` (após sucesso em `deploy-staging`):
   - Deploy para `/Shared/pipeline-medalion-prod`

Cada job de deploy usa Databricks CLI autenticado por variáveis de ambiente.

#### Required GitHub Secrets (por ambiente)

- Ambiente **dev**
  - `DATABRICKS_HOST_DEV`
  - `DATABRICKS_TOKEN_DEV`
- Ambiente **staging**
  - `DATABRICKS_HOST_STAGING`
  - `DATABRICKS_TOKEN_STAGING`
- Ambiente **prod**
  - `DATABRICKS_HOST_PROD`
  - `DATABRICKS_TOKEN_PROD`

Sugestão: configurar GitHub Environments (`dev`, `staging`, `prod`) e associar esses secrets em cada ambiente.

Se for necessário mudar nomes de ambientes ou caminhos de workspace, ajuste as seções `environment:` e os paths `/Shared/pipeline-medalion-<ambiente>` no arquivo `ci-cd.yml`.

---

### Databricks – pré‑requisitos de workspace

Schemas obrigatórios no metastore:

```sql
CREATE SCHEMA bronze;
CREATE SCHEMA silver;
CREATE SCHEMA gold_core;
CREATE SCHEMA gold_ml;
CREATE SCHEMA ml_registry;
```

Além disso:

- Garantir um caminho acessível para o arquivo bruto (por exemplo `/mnt/raw/sales.csv`)
- Criar um Databricks Job apontando para `orchestration/job_entrypoint.py` após o deploy

---

### Configuração de modelos de ML

A definição dos datasets Gold ML é feita em `config/ml_models.json`. Exemplo:

```json
{
  "models": [
    {
      "model_name": "churn_model",
      "version": 1,
      "source_table": "gold_core.customer_metrics",
      "feature_columns": ["frequency", "total_spent", "avg_ticket"],
      "target_column": "frequency"
    }
  ]
}
```

Regras principais:

- `source_table` deve apontar para uma tabela da camada **Gold Core**
- `feature_columns` lista apenas colunas existentes em `source_table`
- `target_column` define a coluna alvo de treino/score
- `version` deve ser incrementada sempre que houver quebra de compatibilidade (novo target, mudança relevante de features etc.)

Para cada modelo, o pipeline gera:

- Tabela `gold_ml.<model_name>_v<version>`
- Registro correspondente na tabela `ml_registry.model_versions`

Detalhes de contratos e responsabilidades estão descritos em `DATA_CONTRACTS_AND_RULES.md`.


Enterprise Medallion Architecture with:

- Bronze / Silver / Gold Core reusable layers
- ML multi-model versioning
- Delta registry
- Databricks Job orchestration
- Pytest automated tests
- GitHub Actions CI/CD pipeline

## CI/CD Flow (multi-ambiente)

1. Push para a branch `main`
2. GitHub Actions executa:
   - Instalação de dependências
   - Execução de testes com `pytest`
3. Após testes, ocorrem os deploys em cadeia:
   - `dev` → workspace path `/Shared/pipeline-medalion-dev`
   - `staging` → workspace path `/Shared/pipeline-medalion-staging`
   - `prod` → workspace path `/Shared/pipeline-medalion-prod`

Os jobs de deploy utilizam o Databricks CLI autenticado via variáveis de ambiente.

## Required GitHub Secrets (por ambiente)

- Ambiente **dev**
  - `DATABRICKS_HOST_DEV`
  - `DATABRICKS_TOKEN_DEV`
- Ambiente **staging**
  - `DATABRICKS_HOST_STAGING`
  - `DATABRICKS_TOKEN_STAGING`
- Ambiente **prod**
  - `DATABRICKS_HOST_PROD`
  - `DATABRICKS_TOKEN_PROD`

Sugestão: configurar GitHub Environments (`dev`, `staging`, `prod`) e associar esses secrets em cada ambiente.

## Como rodar testes localmente

1. Criar (opcional) e ativar um virtualenv
2. Instalar dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Executar:

   ```bash
   pytest
   ```

Os testes atuais validam a estrutura de `config/ml_models.json` e garantem que cada modelo está devidamente configurado.

## Como executar o pipeline localmente

O entrypoint do pipeline é `orchestration/job_entrypoint.py`, que expõe a função `run_pipeline`.

Variáveis de ambiente suportadas:

- `RAW_SALES_PATH`: caminho do CSV de vendas bruto.
  - Default: `/mnt/raw/sales.csv` (montagem típica em Databricks)
- `PIPELINE_CONFIG_PATH`: caminho para o arquivo de configuração dos modelos.
  - Default: `config/ml_models.json`

Exemplo (Linux/macOS):

```bash
export RAW_SALES_PATH="/caminho/para/sales.csv"
export PIPELINE_CONFIG_PATH="config/ml_models.json"
python orchestration/job_entrypoint.py
```

Exemplo (PowerShell no Windows):

```powershell
$env:RAW_SALES_PATH="C:\caminho\para\sales.csv"
$env:PIPELINE_CONFIG_PATH="config/ml_models.json"
python orchestration/job_entrypoint.py
```

> Observação: para executar integralmente as operações Delta Lake fora do Databricks,
> é necessário ter um ambiente Spark com suporte a Delta configurado (por exemplo,
> adicionando `delta-spark` e configurando o `SparkSession` apropriadamente).

## Como gerar o pacote ZIP do projeto

Há um script utilitário em `scripts/package_project.py` que gera um ZIP com o código
e arquivos relevantes, ignorando diretórios de build, cache e metadados de ferramentas.

Execução:

```bash
python scripts/package_project.py
```

Saída esperada:

- Arquivo `dist/nbx-medalion-pipeline.zip` contendo a estrutura do projeto pronta
  para distribuição ou import em outro repositório/workspace.

## Schemas required in Databricks

CREATE SCHEMA bronze;
CREATE SCHEMA silver;
CREATE SCHEMA gold_core;
CREATE SCHEMA gold_ml;
CREATE SCHEMA ml_registry;

After deployment, create a Databricks Job using:
orchestration/job_entrypoint.py
