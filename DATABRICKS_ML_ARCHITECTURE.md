# nbx-medalion-pipeline – Arquitetura Databricks e Plano de ML

Este documento detalha como a **nbx-medalion-pipeline** se encaixa no ecossistema
do **Databricks** e como o fluxo de **Machine Learning** é (e pode ser) organizado
em cima das camadas Medallion.

Para visão geral da arquitetura de sistema, veja `SYSTEM_ARCHITECTURE.md`.  
Para contratos formais de dados, veja `DATA_CONTRACTS_AND_RULES.md`.

---

## 1. Visão Geral em Databricks

Em alto nível, o desenho em Databricks fica assim:

```text
           ┌──────────────────────────────┐
           │        Data Sources          │
           │   CSV / APIs / DB / Events   │
           └─────────────┬────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │  DBFS / Mounts   │
              │ /mnt/raw/sales.* │
              └────────┬─────────┘
                       │
                       ▼
          ┌──────────────────────────────┐
          │   Databricks Job (nbx)      │
          │ orchestration/job_entry...  │
          └─────────────┬───────────────┘
                        │
        ┌───────────────┴────────────────────────────┐
        ▼                                            ▼
 ┌──────────────────┐                       ┌──────────────────┐
 │   Medallion ETL  │                       │      Gold ML     │
 │ Bronze/Silver/   │                       │  Datasets p/ ML  │
 │ Gold Core        │                       │ gold_ml.*_vN     │
 └────────┬─────────┘                       └────────┬─────────┘
          ▼                                          ▼
 ┌──────────────────┐                       ┌──────────────────┐
 │   Delta Tables   │                       │   ML Registry    │
 │ bronze/silver/   │                       │ ml_registry.*    │
 │ gold_core/gold_ml│                       └──────────────────┘
 └──────────────────┘
```

Componentes chave no workspace:

- **Schemas Delta**: `bronze`, `silver`, `gold_core`, `gold_ml`, `ml_registry`.
- **Job Databricks**: chama `orchestration/job_entrypoint.py`.
- **Storage bruto**: montagens/paths como `/mnt/raw/sales.csv`.
- **Cluster**: executa o Spark que lê/escreve todas as camadas.

---

## 2. Fluxo do Job nbx-medalion-pipeline em Databricks

O job principal roda o script:

- `orchestration/job_entrypoint.py`

Comportamento:

1. Lê variáveis de ambiente opcionais:
   - `RAW_SALES_PATH` (default `/mnt/raw/sales.csv`)
   - `PIPELINE_CONFIG_PATH` (default `config/ml_models.json`)
2. Executa em sequência:
   1. **Bronze** – `ingest_raw("sales_raw", RAW_SALES_PATH)`
      - Lê CSV bruto e grava `bronze.sales_raw`.
   2. **Silver** – `transform_sales()`
      - Limpa/filtra e grava `silver.sales_clean`.
   3. **Gold Core** – `build_customer_metrics()`
      - Agrega métricas por cliente e grava `gold_core.customer_metrics`.
   4. **Gold ML** – `generate_models(PIPELINE_CONFIG_PATH)`
      - Lê `config/ml_models.json`, gera `gold_ml.<model>_v<version>` e registra
        as versões em `ml_registry.model_versions`.

Em Databricks, esse job pode ser:

- **Agendado** (schedule) para rodar periodicamente.
- **Disparado via CI/CD**, após o deploy de código feito pelo GitHub Actions.

---

## 3. Desenho Detalhado das Camadas no Databricks

### 3.1 Camadas Delta no metastore

```text
catálogo / metastore (padrão)
│
├── bronze
│   └── sales_raw
│
├── silver
│   └── sales_clean
│
├── gold_core
│   └── customer_metrics
│
├── gold_ml
│   ├── churn_model_v1
│   └── clv_model_v2
│
└── ml_registry
    └── model_versions
```

### 3.2 Relacionamento com o código da nbx-medalion-pipeline

- `src/bronze/bronze_ingestion.py` → escreve em `bronze.*`
- `src/silver/silver_transformation.py` → escreve em `silver.*`
- `src/gold_core/gold_core_builder.py` → escreve em `gold_core.*`
- `src/ml/gold_ml_generator.py` → escreve em `gold_ml.*`
- `src/registry/model_registry.py` → escreve em `ml_registry.model_versions`

Esse mapeamento é importante para manter o **contrato entre Databricks e código**
sempre explícito.

---

## 4. Plano de ML sobre a nbx-medalion-pipeline

Atualmente, o projeto está focado em:

- Preparar datasets de alta qualidade (Gold Core).
- Gerar **datasets especializados por modelo** (Gold ML).
- Manter um **registry simples de versões de datasets** para ML.

Abaixo está um plano de evolução natural do fluxo de ML sobre essa base.

### 4.1 Fase 1 – Datasets de Treino/Score (já coberta)

1. **Definição de modelos** em `config/ml_models.json`:
   - `model_name`, `version`, `source_table`, `feature_columns`, `target_column`.
2. **Execução do job nbx**:
   - Gera `gold_ml.<model_name>_v<version>`.
   - Registra a versão em `ml_registry.model_versions`.
3. **Uso pelos times de ML**:
   - Cientistas de dados conectam notebooks ao Databricks e usam as tabelas
     `gold_ml.*` como fonte única de datasets para treino/validação.

### 4.2 Fase 2 – Treinamento de Modelos (extensão sugerida)

Com os datasets Gold ML prontos, o próximo passo é padronizar o treinamento:

```text
gold_ml.<model>_vN  ──► Notebook/Job de Treino  ──► Modelo treinado (MLflow)
```

Proposta:

- Criar um **notebook de treino por tipo de modelo** ou um script parametrizado, por exemplo:
  - `ml_training/train_model.py --model_name churn_model --version 1`
- Integrar com **MLflow** para:
  - Registrar parâmetros, métricas e artefatos de modelos.
  - Versioar modelos treinados (não apenas datasets).
- Ligar cada execução de treino a:
  - Uma entrada em `ml_registry.model_versions` (dataset usado).
  - Um registro em MLflow (modelo treinado).

### 4.3 Fase 3 – Promoção entre ambientes (dev → staging → prod)

Usando a mesma estrutura de ambientes do CI/CD:

1. **dev**:
   - Geração e teste de novos datasets Gold ML.
   - Treino de modelos experimentais.
2. **staging**:
   - Reprocesso (ou replicação) dos datasets Gold ML aprovados.
   - Treino/validação com dados próximos de produção.
3. **prod**:
   - Consumo de datasets Gold ML estáveis.
   - Deploy de modelos “aprovados” de MLflow para endpoints/Jobs de scoring.

O registry `ml_registry.model_versions` pode ser usado como **ponte** para saber
quais versões de datasets estão implantadas e em qual ambiente.

### 4.4 Fase 4 – Monitoramento e Re-treino

Com o pipeline estabilizado:

- Monitorar:
  - Qualidade dos dados em Gold Core / Gold ML.
  - Métricas de performance dos modelos em produção.
- Disparar re-treinos:
  - Com base em janelas de tempo (ex.: mensal).
  - Ou em degradação de métricas.

O desenho fica:

```text
Gold Core ──► Gold ML ──► Treino (MLflow) ──► Deploy ──► Monitoramento
                 ▲                                  │
                 └────────────── Re-treino ◄────────┘
```

---

## 5. Integração com o CI/CD

O pipeline GitHub Actions da **nbx-medalion-pipeline** cuida de:

- **Build + Test**:
  - Conferir que o código e `ml_models.json` estão válidos.
- **Deploy de código** para:
  - `/Shared/pipeline-medalion-dev`
  - `/Shared/pipeline-medalion-staging`
  - `/Shared/pipeline-medalion-prod`

Em uma evolução natural, você pode:

- Adicionar etapas no CI/CD para:
  - Disparar (via API) Jobs de treino em Databricks após atualizar dados/código.
  - Validar automaticamente se novos modelos atingem métricas mínimas antes
    de serem promovidos.

---

## 6. Resumo

- A **nbx-medalion-pipeline** organiza o plano de ML começando por onde mais dói:
  - **dados de qualidade e versionados**.
- Em Databricks:
  - O Job principal constrói as camadas Bronze/Silver/Gold Core/Gold ML.
  - O registry Delta (`ml_registry.model_versions`) oferece rastreio de versões.
- O plano de ML se apoia nisso para:
  - Padronizar datasets de treino,
  - Padronizar treinamento (MLflow),
  - Controlar promoção entre ambientes via Databricks + GitHub Actions.

Com esse desenho, fica claro **onde o Databricks entra**, **onde o código da nbx-medalion-pipeline atua**
e **como o ciclo de vida de ML pode evoluir de forma incremental e governada**.

