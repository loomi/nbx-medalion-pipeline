
"""
Módulo da camada Gold ML.

Responsável por, a partir de configurações declarativas em JSON,
gerar datasets específicos por modelo de ML (`gold_ml.<model>_v<version>`)
e registrar cada versão gerada no registry Delta.
"""

import json
from pyspark.sql import SparkSession
from registry.model_registry import register_model_version

spark = SparkSession.builder.getOrCreate()


def generate_models(config_path: str):
    """
    Lê o arquivo de configuração de modelos (`ml_models.json` ou similar),
    cria datasets de features+target para cada modelo definido e grava
    cada dataset em `gold_ml.<model_name>_v<version>`, registrando também
    a versão correspondente no `ml_registry.model_versions`.
    """
    with open(config_path, "r") as f:
        configs = json.load(f)

    for model in configs["models"]:
        model_name = model["model_name"]
        version = model["version"]

        df = spark.table(model["source_table"])

        selected = df.select(model["feature_columns"] + [model["target_column"]])

        table_name = f"gold_ml.{model_name}_v{version}"

        (
            selected.write.format("delta")
            .mode("overwrite")
            .saveAsTable(table_name)
        )

        register_model_version(model_name, version)
