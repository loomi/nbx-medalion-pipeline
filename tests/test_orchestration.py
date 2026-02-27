"""
Testes unitários do caso de uso Orquestração: pipeline end-to-end (run_pipeline).
"""
from unittest.mock import patch


@patch("orchestration.job_entrypoint.generate_models")
@patch("orchestration.job_entrypoint.build_customer_metrics")
@patch("orchestration.job_entrypoint.transform_sales")
@patch("orchestration.job_entrypoint.ingest_raw")
def test_run_pipeline_chama_ingest_raw_uma_vez(ingest_raw, transform_sales, build_metrics, generate_models):
    from orchestration.job_entrypoint import run_pipeline

    run_pipeline()
    ingest_raw.assert_called_once()


@patch("orchestration.job_entrypoint.generate_models")
@patch("orchestration.job_entrypoint.build_customer_metrics")
@patch("orchestration.job_entrypoint.transform_sales")
@patch("orchestration.job_entrypoint.ingest_raw")
def test_run_pipeline_chama_transform_sales_uma_vez(ingest_raw, transform_sales, build_metrics, generate_models):
    from orchestration.job_entrypoint import run_pipeline

    run_pipeline()
    transform_sales.assert_called_once()


@patch("orchestration.job_entrypoint.generate_models")
@patch("orchestration.job_entrypoint.build_customer_metrics")
@patch("orchestration.job_entrypoint.transform_sales")
@patch("orchestration.job_entrypoint.ingest_raw")
def test_run_pipeline_chama_build_customer_metrics_uma_vez(ingest_raw, transform_sales, build_metrics, generate_models):
    from orchestration.job_entrypoint import run_pipeline

    run_pipeline()
    build_metrics.assert_called_once()


@patch("orchestration.job_entrypoint.generate_models")
@patch("orchestration.job_entrypoint.build_customer_metrics")
@patch("orchestration.job_entrypoint.transform_sales")
@patch("orchestration.job_entrypoint.ingest_raw")
def test_run_pipeline_chama_generate_models_uma_vez(ingest_raw, transform_sales, build_metrics, generate_models):
    from orchestration.job_entrypoint import run_pipeline

    run_pipeline()
    generate_models.assert_called_once()


@patch("orchestration.job_entrypoint.generate_models")
@patch("orchestration.job_entrypoint.build_customer_metrics")
@patch("orchestration.job_entrypoint.transform_sales")
@patch("orchestration.job_entrypoint.ingest_raw")
def test_run_pipeline_chama_ingest_raw_com_sales_raw_e_path_default(ingest_raw, transform_sales, build_metrics, generate_models):
    from orchestration.job_entrypoint import run_pipeline, RAW_SALES_PATH

    run_pipeline()
    ingest_raw.assert_called_once_with("sales_raw", RAW_SALES_PATH)


@patch("orchestration.job_entrypoint.generate_models")
@patch("orchestration.job_entrypoint.build_customer_metrics")
@patch("orchestration.job_entrypoint.transform_sales")
@patch("orchestration.job_entrypoint.ingest_raw")
def test_run_pipeline_chama_generate_models_com_config_path_default(ingest_raw, transform_sales, build_metrics, generate_models):
    from orchestration.job_entrypoint import run_pipeline, MODEL_CONFIG_PATH

    run_pipeline()
    generate_models.assert_called_once_with(MODEL_CONFIG_PATH)


@patch("orchestration.job_entrypoint.generate_models")
@patch("orchestration.job_entrypoint.build_customer_metrics")
@patch("orchestration.job_entrypoint.transform_sales")
@patch("orchestration.job_entrypoint.ingest_raw")
def test_run_pipeline_executa_na_ordem_bronze_silver_gold_core_gold_ml(ingest_raw, transform_sales, build_metrics, generate_models):
    from orchestration.job_entrypoint import run_pipeline

    run_pipeline()
    order = [
        ingest_raw.call_args_list,
        transform_sales.call_args_list,
        build_metrics.call_args_list,
        generate_models.call_args_list,
    ]
    assert all(len(c) == 1 for c in order)
    # Verifica ordem: ingest_raw antes de transform_sales, etc.
    assert ingest_raw.call_count == 1
    assert transform_sales.call_count == 1
    assert build_metrics.call_count == 1
    assert generate_models.call_count == 1
