"""
Testes unitários do caso de uso Bronze: ingestão bruta (ingest_raw).
"""
import pytest
from unittest.mock import MagicMock, patch


@patch("bronze.bronze_ingestion.spark")
def test_ingest_raw_lê_csv_do_path_informado(mock_spark):
    mock_read = MagicMock()
    mock_df = MagicMock()
    mock_spark.read.format.return_value.option.return_value.option.return_value.load.return_value = mock_df

    from bronze.bronze_ingestion import ingest_raw

    ingest_raw("sales_raw", "/mnt/raw/sales.csv")

    mock_spark.read.format.assert_called_once_with("csv")
    mock_spark.read.format.return_value.option.assert_any_call("header", True)
    mock_spark.read.format.return_value.option.return_value.option.assert_any_call("inferSchema", True)
    mock_spark.read.format.return_value.option.return_value.option.return_value.load.assert_called_once_with(
        "/mnt/raw/sales.csv"
    )


@patch("bronze.bronze_ingestion.spark")
def test_ingest_raw_grava_na_tabela_bronze_com_nome_correto(mock_spark):
    mock_df = MagicMock()
    mock_spark.read.format.return_value.option.return_value.option.return_value.load.return_value = mock_df

    from bronze.bronze_ingestion import ingest_raw

    ingest_raw("sales_raw", "/any/path.csv")

    mock_df.write.format.assert_called_once_with("delta")
    mock_df.write.format.return_value.mode.assert_called_once_with("overwrite")
    mock_df.write.format.return_value.mode.return_value.saveAsTable.assert_called_once_with("bronze.sales_raw")


@patch("bronze.bronze_ingestion.spark")
def test_ingest_raw_usa_nome_da_tabela_parametrizado(mock_spark):
    mock_df = MagicMock()
    mock_spark.read.format.return_value.option.return_value.option.return_value.load.return_value = mock_df

    from bronze.bronze_ingestion import ingest_raw

    ingest_raw("outra_tabela", "/mnt/raw/outro.csv")

    mock_df.write.format.return_value.mode.return_value.saveAsTable.assert_called_once_with("bronze.outra_tabela")
