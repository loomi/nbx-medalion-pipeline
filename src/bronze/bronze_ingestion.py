
"""
Módulo da camada Bronze.

Responsável por ingerir arquivos brutos (por exemplo, CSV de vendas)
e gravá-los como tabelas Delta na camada `bronze`, sem aplicar regras
de negócio ou transformações complexas.
"""

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()


def ingest_raw(table_name: str, path: str):
    """
    Lê um arquivo CSV bruto e grava seu conteúdo como uma tabela Delta
    na camada Bronze (`bronze.<table_name>`), preservando a estrutura
    de colunas da fonte.
    """
    df = (
        spark.read.format("csv")
        .option("header", True)
        .option("inferSchema", True)
        .load(path)
    )

    (
        df.write.format("delta")
        .mode("overwrite")
        .saveAsTable(f"bronze.{table_name}")
    )
