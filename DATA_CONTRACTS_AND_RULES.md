# nbx-medalion-pipeline – Data Contracts and Rules

O objetivo deste documento é definir os **contratos formais de dados**
da plataforma **nbx-medalion-pipeline**, estabelecendo:

- Responsabilidades por camada da Arquitetura Medallion.
- Garantias de entrada e saída.
- Regras de versionamento e registry.
- Limites claros entre Engenharia de Dados e Machine Learning.

Para entender o contexto arquitetural completo, consulte também `SYSTEM_ARCHITECTURE.md`.

---

## 1. Objetivo

Este contrato deve ser respeitado por todos os times que produzem ou consomem
dados dentro da **nbx-medalion-pipeline**.

Ele formaliza:

- **Responsabilidades por camada** (Bronze, Silver, Gold Core, Gold ML, Registry).
- **Garantias mínimas** de qualidade e integridade.
- **Regras de versionamento** de datasets de ML.
- **Governança** entre times de Engenharia de Dados, ML e Plataforma.

---

## 2. Contrato Bronze

### 2.1 Responsabilidade

Ingestão bruta dos dados **exatamente como recebidos** da origem.

### 2.2 Garantias

- Estrutura idêntica à fonte (colunas, tipos brutos).
- Nenhuma regra de negócio aplicada.
- Persistência em Delta Lake no schema `bronze`.
- Rastreabilidade do caminho de origem.

### 2.3 Proibições

- Não aplicar agregações.
- Não alterar nomes de colunas.
- Não excluir registros da ingestão bruta.

### 2.4 Entrada Esperada

- Arquivos brutos, por exemplo:
  - `/mnt/raw/sales.csv`

### 2.5 Saída Garantida

- Tabelas no padrão:
  - `bronze.<table_name>`

Exemplo concreto do projeto:

- Entrada: `/mnt/raw/sales.csv`
- Saída: `bronze.sales_raw`

---

## 3. Contrato Silver

### 3.1 Responsabilidade

Camada de **limpeza**, **padronização** e **validações básicas**.

### 3.2 Garantias

- Remoção de registros inválidos (ex.: `customer_id` nulo).
- Tipos de dados padronizados e coerentes.
- Regras básicas de integridade (por exemplo, chaves obrigatórias).
- Dados prontos para consumo interno (eng. de dados, relatórios, Gold Core).

### 3.3 Proibições

- Não criar métricas consolidadas de negócio.
- Não aplicar lógica específica de modelos de ML.

### 3.4 Entrada

- Tabelas da camada Bronze:
  - `bronze.<table>`

### 3.5 Saída

- Tabelas da camada Silver:
  - `silver.<table_clean>`

Exemplo concreto:

- Entrada: `bronze.sales_raw`
- Saída: `silver.sales_clean`

---

## 4. Contrato Gold Core

### 4.1 Responsabilidade

Camada de **métricas de negócio consolidadas** e **reutilizáveis**.

### 4.2 Garantias

- Dados agregados segundo o domínio de negócio.
- Estável e **independente de modelos de ML**.
- Estrutura orientada a negócio (ex.: cliente, produto, canal).
- Pode ser consumida por múltiplos times e aplicações.

### 4.3 Proibições

- Não conter features específicas de um único modelo de ML.
- Não conter lógica experimental ou temporária.

### 4.4 Entrada

- Tabelas da camada Silver:
  - `silver.<table>`

### 4.5 Saída

- Tabelas da camada Gold Core:
  - `gold_core.<domain_metric>`

Exemplo concreto:

- Entrada: `silver.sales_clean`
- Saída: `gold_core.customer_metrics`

---

## 5. Contrato Gold ML

### 5.1 Responsabilidade

Gerar **datasets específicos por modelo de ML**, sempre
derivados da camada Gold Core e **versionados**.

### 5.2 Regras Obrigatórias

- Versionamento obrigatório por modelo (`version`).
- Definição totalmente declarativa via JSON (`config/ml_models.json`).
- Registro automático no registry Delta (`ml_registry.model_versions`).
- Proibido alterar a Gold Core diretamente a partir desta camada.

### 5.3 Entrada

- Tabelas da camada Gold Core:
  - `gold_core.<table>`
- Arquivo de configuração:
  - `config/ml_models.json`

### 5.4 Saída

- Tabelas da camada Gold ML:
  - `gold_ml.<model_name>_v<version>`

### 5.5 Registry

- Tabela:
  - `ml_registry.model_versions`
- Cada linha representa uma versão de dataset gerado para um modelo.

---

## 6. Contrato de Configuração de Modelos (`ml_models.json`)

Cada modelo de ML é definido em `config/ml_models.json`.

Estrutura mínima por modelo:

```json
{
  "model_name": "nome_do_modelo",
  "version": 1,
  "source_table": "gold_core.tabela_origem",
  "feature_columns": ["col1", "col2"],
  "target_column": "col_target"
}
```

Regras:

- `model_name`: identificador único legível do modelo.
- `version`: número inteiro crescente (1, 2, 3, ...).
- `source_table`: **sempre** uma tabela da camada Gold Core.
- `feature_columns`: lista de colunas de features existentes em `source_table`.
- `target_column`: coluna alvo do modelo (ex.: churn, CLV, etc.).

O arquivo completo segue o formato:

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

---

## 7. Contrato de Versionamento de Modelos

Todo modelo na **nbx-medalion-pipeline** deve declarar
explicitamente sua versão:

```json
{
  "model_name": "nome",
  "version": 1
}
```

### 7.1 Regras

- **Nova feature** relevante → **nova versão**.
- **Mudança de target** → **nova versão**.
- Versões não devem ser sobrescritas.
- Histórico de versões deve ser preservado.

### 7.2 Registry

Para cada versão gerada, é criado um registro em:

- `ml_registry.model_versions`

Esse registry funciona como fonte de verdade para:

- Quais modelos/datasets existem.
- Quais versões foram geradas e quando.
- Auditoria e rastreabilidade de experimentos e produção.

---

## 8. Responsabilidades Organizacionais

| Camada     | Responsável      | Tipo de Governança |
|-----------|------------------|---------------------|
| Bronze    | Engenharia de Dados | Técnica          |
| Silver    | Engenharia de Dados | Técnica          |
| Gold Core | Engenharia de Dados | Negócio          |
| Gold ML   | ML + Engenharia de Dados | Controlada |
| Registry  | Plataforma        | Automática         |

Principais pontos:

- **Engenharia de Dados** é dona das camadas Bronze, Silver e Gold Core.
- **ML** configura e consome Gold ML, respeitando os contratos com Gold Core.
- **Plataforma** garante CI/CD, ambientes, secrets e registry.

---

## 9. Auditoria e Conformidade

Todos os dados da **nbx-medalion-pipeline** são armazenados em Delta Lake,
permitindo:

- Versionamento de tabelas (time travel).
- Rastreabilidade de mudanças.
- Auditoria de quem gerou/atualizou cada dataset.

Políticas de retenção, acesso e compliance podem ser implementadas sobre
essas capacidades de Delta + metastore.

---

## 10. Violação de Contrato

Qualquer alteração que viole as regras definidas neste documento deve:

- Ser identificada e revisada.
- Gerar **nova versão** (quando aplicável).
- Ser documentada em nível de mudança (ex.: changelog, PR, ticket).
- Ter aprovação explícita do time responsável pela camada afetada.

---

## 11. Princípio Fundamental

- **Gold Core é reutilizável** e estável.
- **Gold ML é descartável e versionado**.

Esse princípio garante:

- Escalabilidade com múltiplos modelos simultâneos.
- Governança clara entre dados de negócio e datasets específicos de ML.
- Evolução controlada da plataforma **nbx-medalion-pipeline**.

