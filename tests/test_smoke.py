from pathlib import Path

from src.data import dataset_summary, load_comments
from src.modeling import compare_models


def test_sample_data_loads():
    frame = load_comments("data/sample_train.csv")
    summary = dataset_summary(frame)
    assert summary["rows"] == 24
    assert summary["toxic_comments"] == 10


def test_pipeline_creates_artifacts(tmp_path: Path):
    frame = load_comments("data/sample_train.csv")
    results = compare_models(frame, tmp_path, test_size=0.25)
    assert len(results) == 2
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "confusion_matrix.png").exists()
