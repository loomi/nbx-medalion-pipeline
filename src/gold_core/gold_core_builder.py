
"""
Módulo da camada Gold Core.

Responsável por calcular métricas de negócio reutilizáveis (por exemplo,
métricas por cliente) a partir da camada Silver e gravá-las na camada
`gold_core`, sem lógica específica de um único modelo de ML.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import count, sum, avg

spark = SparkSession.builder.getOrCreate()


def build_customer_metrics():
    """
    Lê a tabela `silver.sales_clean`, agrega vendas por `customer_id` e
    calcula frequência de compras, valor total gasto e ticket médio,
    gravando o resultado em `gold_core.customer_metrics`.
    """
    df = spark.table("silver.sales_clean")

    gold_df = df.groupBy("customer_id").agg(
        count("*").alias("frequency"),
        sum("amount").alias("total_spent"),
        avg("amount").alias("avg_ticket"),
    )

    (
        gold_df.write.format("delta")
        .mode("overwrite")
        .saveAsTable("gold_core.customer_metrics")
    )
