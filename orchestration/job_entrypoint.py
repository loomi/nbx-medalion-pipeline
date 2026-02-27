
"""
Entrypoint de orquestração do pipeline Medallion + ML.

Responsável por encadear as etapas Bronze → Silver → Gold Core → Gold ML
utilizando os módulos de cada camada e variáveis de ambiente para paths
de dados brutos e configuração de modelos.
"""

import os
import sys
from pathlib import Path

# Garante que a pasta `src` esteja no PYTHONPATH para permitir imports
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from bronze.bronze_ingestion import ingest_raw
from silver.silver_transformation import transform_sales
from gold_core.gold_core_builder import build_customer_metrics
from gold_ml.gold_ml_generator import generate_models

RAW_SALES_PATH = os.getenv("RAW_SALES_PATH", "/mnt/raw/sales.csv")
MODEL_CONFIG_PATH = os.getenv("PIPELINE_CONFIG_PATH", "config/ml_models.json")


def run_pipeline():
    """
    Executa o pipeline fim a fim em ordem:
    1. Bronze: ingere dados brutos em `bronze.sales_raw`;
    2. Silver: limpa e grava `silver.sales_clean`;
    3. Gold Core: calcula métricas de negócio em `gold_core.customer_metrics`;
    4. Gold ML: gera datasets específicos por modelo conforme a configuração.
    """
    ingest_raw("sales_raw", RAW_SALES_PATH)
    transform_sales()
    build_customer_metrics()
    generate_models(MODEL_CONFIG_PATH)


if __name__ == "__main__":
    run_pipeline()
