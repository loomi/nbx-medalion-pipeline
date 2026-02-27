"""
Testes unitários do caso de uso Gold Core: métricas de negócio (build_customer_metrics).
"""
from unittest.mock import MagicMock, patch


@patch("gold_core.gold_core_builder.spark")
def test_build_customer_metrics_lê_silver_sales_clean(mock_spark):
    mock_df = MagicMock()
    mock_grouped = MagicMock()
    mock_spark.table.return_value = mock_df
    mock_df.groupBy.return_value.agg.return_value = mock_grouped

    from gold_core.gold_core_builder import build_customer_metrics

    build_customer_metrics()

    mock_spark.table.assert_called_once_with("silver.sales_clean")


@patch("gold_core.gold_core_builder.spark")
def test_build_customer_metrics_agrega_por_customer_id(mock_spark):
    mock_df = MagicMock()
    mock_grouped = MagicMock()
    mock_spark.table.return_value = mock_df
    mock_df.groupBy.return_value.agg.return_value = mock_grouped

    from gold_core.gold_core_builder import build_customer_metrics

    build_customer_metrics()

    mock_df.groupBy.assert_called_once_with("customer_id")


@patch("gold_core.gold_core_builder.spark")
def test_build_customer_metrics_grava_em_gold_core_customer_metrics(mock_spark):
    mock_df = MagicMock()
    mock_grouped = MagicMock()
    mock_spark.table.return_value = mock_df
    mock_df.groupBy.return_value.agg.return_value = mock_grouped

    from gold_core.gold_core_builder import build_customer_metrics

    build_customer_metrics()

    mock_grouped.write.format.assert_called_once_with("delta")
    mock_grouped.write.format.return_value.mode.assert_called_once_with("overwrite")
    mock_grouped.write.format.return_value.mode.return_value.saveAsTable.assert_called_once_with(
        "gold_core.customer_metrics"
    )
