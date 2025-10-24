import os
from retrain_agent import retrain_if_needed, MODELS_DIR, MODEL_CARDS_DIR


def test_retrain_creates_artifacts(tmp_path):
    # Run retraining (reads CSV from repo root). This is a smoke test.
    result = retrain_if_needed()

    assert isinstance(result, dict)
    assert "auc" in result
    assert "artifacts" in result

    artifacts = result["artifacts"]
    # Check model files exist on disk
    for key in ("model", "scaler", "features"):
        path = artifacts.get(key)
        assert path is not None
        assert os.path.exists(path), f"Expected artifact {path} to exist"

    # Check model card was created
    mc = result.get("model_card")
    assert mc and isinstance(mc, dict)
    assert os.path.exists(mc.get("markdown"))
    assert os.path.exists(mc.get("html"))
