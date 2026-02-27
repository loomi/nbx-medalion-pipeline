"""
Testes unitários do caso de uso Registry: registro de versões de modelos (register_model_version).
"""
from unittest.mock import MagicMock, patch


@patch("registry.model_registry.spark")
def test_register_model_version_cria_dataframe_com_model_name_e_version(mock_spark):
    mock_df = MagicMock()
    mock_with_ts = MagicMock()
    mock_spark.createDataFrame.return_value.withColumn.return_value = mock_with_ts

    from registry.model_registry import register_model_version

    register_model_version("churn_model", 1)

    mock_spark.createDataFrame.assert_called_once()
    call_args = mock_spark.createDataFrame.call_args
    data, schema = call_args[0][0], call_args[0][1]
    assert data == [("churn_model", 1)]
    assert schema == ["model_name", "version"]


@patch("registry.model_registry.spark")
def test_register_model_version_grava_em_ml_registry_model_versions(mock_spark):
    mock_df = MagicMock()
    mock_with_ts = MagicMock()
    mock_spark.createDataFrame.return_value.withColumn.return_value = mock_with_ts

    from registry.model_registry import register_model_version

    register_model_version("clv_model", 2)

    mock_with_ts.write.format.assert_called_once_with("delta")
    mock_with_ts.write.format.return_value.mode.assert_called_once_with("append")
    mock_with_ts.write.format.return_value.mode.return_value.saveAsTable.assert_called_once_with(
        "ml_registry.model_versions"
    )


@patch("registry.model_registry.spark")
def test_register_model_version_usa_modo_append(mock_spark):
    mock_df = MagicMock()
    mock_with_ts = MagicMock()
    mock_spark.createDataFrame.return_value.withColumn.return_value = mock_with_ts

    from registry.model_registry import register_model_version

    register_model_version("any_model", 3)

    mock_with_ts.write.format.return_value.mode.assert_called_once_with("append")
