
"""
Módulo de registry de modelos de ML.

Responsável por registrar em uma tabela Delta (`ml_registry.model_versions`)
cada versão de dataset/modelo gerada pela camada Gold ML, com timestamp
de registro para auditoria e rastreabilidade.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp

spark = SparkSession.builder.getOrCreate()


def register_model_version(model_name: str, version: int):
    """
    Cria um registro simples com `model_name`, `version` e `registered_at`
    e o adiciona (modo append) à tabela `ml_registry.model_versions`.
    """
    data = [(model_name, version)]
    df = (
        spark.createDataFrame(data, ["model_name", "version"])
        .withColumn("registered_at", current_timestamp())
    )

    (
        df.write.format("delta")
        .mode("append")
        .saveAsTable("ml_registry.model_versions")
    )
