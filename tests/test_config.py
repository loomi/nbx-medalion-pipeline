
import json


def _load_models():
    with open("config/ml_models.json") as f:
        data = json.load(f)
    return data["models"]


def test_model_config_structure():
    with open("config/ml_models.json") as f:
        data = json.load(f)

    assert "models" in data
    assert isinstance(data["models"], list)


def test_model_has_version():
    models = _load_models()

    for model in models:
        assert "version" in model


def test_model_has_required_fields():
    models = _load_models()
    required_fields = {"model_name", "source_table", "feature_columns", "target_column"}

    for model in models:
        missing = required_fields.difference(model.keys())
        assert not missing, f"Missing fields in model config: {missing}"
        assert isinstance(model["feature_columns"], list)
        assert model["feature_columns"], "feature_columns should not be empty"
