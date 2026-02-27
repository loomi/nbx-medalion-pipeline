"""
Testes unitários do caso de uso Silver: transformação e limpeza (transform_sales).
"""
from unittest.mock import MagicMock, patch


@patch("silver.silver_transformation.spark")
def test_transform_sales_lê_tabela_bronze_sales_raw(mock_spark):
    mock_df = MagicMock()
    mock_filtered = MagicMock()
    mock_spark.table.return_value = mock_df
    mock_df.filter.return_value = mock_filtered

    from silver.silver_transformation import transform_sales

    transform_sales()

    mock_spark.table.assert_called_once_with("bronze.sales_raw")


@patch("silver.silver_transformation.spark")
def test_transform_sales_filtra_registros_invalidos(mock_spark):
    mock_df = MagicMock()
    mock_filtered = MagicMock()
    mock_spark.table.return_value = mock_df
    mock_df.filter.return_value = mock_filtered

    from silver.silver_transformation import transform_sales

    transform_sales()

    mock_df.filter.assert_called_once()


@patch("silver.silver_transformation.spark")
def test_transform_sales_grava_em_silver_sales_clean(mock_spark):
    mock_df = MagicMock()
    mock_filtered = MagicMock()
    mock_spark.table.return_value = mock_df
    mock_df.filter.return_value = mock_filtered

    from silver.silver_transformation import transform_sales

    transform_sales()

    mock_filtered.write.format.assert_called_once_with("delta")
    mock_filtered.write.format.return_value.mode.assert_called_once_with("overwrite")
    mock_filtered.write.format.return_value.mode.return_value.saveAsTable.assert_called_once_with("silver.sales_clean")
