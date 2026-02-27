"""
Testes unitários do caso de uso Gold ML: geração de datasets por modelo (generate_models).
"""
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


@patch("gold_ml.gold_ml_generator.register_model_version")
@patch("gold_ml.gold_ml_generator.spark")
def test_generate_models_lê_config_e_grava_tabelas_gold_ml(mock_spark, mock_register):
    config = {
        "models": [
            {
                "model_name": "churn_model",
                "version": 1,
                "source_table": "gold_core.customer_metrics",
                "feature_columns": ["frequency", "total_spent"],
                "target_column": "avg_ticket",
            }
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        config_path = f.name

    mock_df = MagicMock()
    mock_selected = MagicMock()
    mock_spark.table.return_value = mock_df
    mock_df.select.return_value = mock_selected

    try:
        from gold_ml.gold_ml_generator import generate_models

        generate_models(config_path)
        mock_spark.table.assert_called_with("gold_core.customer_metrics")
        mock_df.select.assert_called_once()
        cols = mock_df.select.call_args[0][0]
        assert cols == ["frequency", "total_spent", "avg_ticket"]
        mock_selected.write.format.return_value.mode.return_value.saveAsTable.assert_called_once_with(
            "gold_ml.churn_model_v1"
        )
        mock_register.assert_called_once_with("churn_model", 1)
    finally:
        Path(config_path).unlink(missing_ok=True)


@patch("gold_ml.gold_ml_generator.register_model_version")
@patch("gold_ml.gold_ml_generator.spark")
def test_generate_models_registra_cada_versao_no_registry(mock_spark, mock_register):
    config = {
        "models": [
            {"model_name": "m1", "version": 1, "source_table": "gold_core.x", "feature_columns": ["a"], "target_column": "b"},
            {"model_name": "m2", "version": 2, "source_table": "gold_core.x", "feature_columns": ["a"], "target_column": "b"},
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        config_path = f.name

    mock_df = MagicMock()
    mock_selected = MagicMock()
    mock_spark.table.return_value = mock_df
    mock_df.select.return_value = mock_selected

    try:
        from gold_ml.gold_ml_generator import generate_models

        generate_models(config_path)
        assert mock_register.call_count == 2
        mock_register.assert_any_call("m1", 1)
        mock_register.assert_any_call("m2", 2)
    finally:
        Path(config_path).unlink(missing_ok=True)


@patch("gold_ml.gold_ml_generator.register_model_version")
@patch("gold_ml.gold_ml_generator.spark")
def test_generate_models_usa_nome_tabela_gold_ml_model_v_version(mock_spark, mock_register):
    config = {
        "models": [
            {"model_name": "clv_model", "version": 3, "source_table": "gold_core.metrics", "feature_columns": ["x"], "target_column": "y"}
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config, f)
        config_path = f.name

    mock_df = MagicMock()
    mock_selected = MagicMock()
    mock_spark.table.return_value = mock_df
    mock_df.select.return_value = mock_selected

    try:
        from gold_ml.gold_ml_generator import generate_models

        generate_models(config_path)
        mock_selected.write.format.return_value.mode.return_value.saveAsTable.assert_called_once_with(
            "gold_ml.clv_model_v3"
        )
    finally:
        Path(config_path).unlink(missing_ok=True)
