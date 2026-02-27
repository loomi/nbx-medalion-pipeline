"""
Módulo da camada Silver.

Responsável por ler dados brutos da camada Bronze, aplicar regras de
limpeza/qualidade básicas (como remoção de registros inválidos) e
gravar o resultado como tabela Delta na camada `silver`.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.getOrCreate()


def transform_sales():
    """
    Lê a tabela `bronze.sales_raw`, remove registros com `customer_id`
    nulo e grava o resultado limpo na tabela `silver.sales_clean`.
    """
    df = spark.table("bronze.sales_raw")
    cleaned = df.filter(col("customer_id").isNotNull())

    (
        cleaned.write.format("delta")
        .mode("overwrite")
        .saveAsTable("silver.sales_clean")
    )
