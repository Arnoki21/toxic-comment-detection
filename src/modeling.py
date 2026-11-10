from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, average_precision_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from .config import RANDOM_STATE


def build_models() -> dict[str, Pipeline]:
    classifier = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)
    return {
        "word_tfidf_lr": Pipeline([
            ("features", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=80_000, sublinear_tf=True)),
            ("classifier", classifier),
        ]),
        "word_char_tfidf_lr": Pipeline([
            ("features", FeatureUnion([
                ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=80_000, sublinear_tf=True)),
                ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, max_features=80_000, sublinear_tf=True)),
            ])),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)),
        ]),
    }


def _metrics(y_true: pd.Series, probabilities: np.ndarray, model_name: str) -> dict:
    predicted = (probabilities >= 0.5).astype(int)
    return {
        "model_name": model_name,
        "vectorizer": "word 1-2 gram TF-IDF" if model_name == "word_tfidf_lr" else "word 1-2 gram + character 3-5 gram TF-IDF",
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "pr_auc": float(average_precision_score(y_true, probabilities)),
        "precision": float(precision_score(y_true, predicted, zero_division=0)),
        "recall": float(recall_score(y_true, predicted, zero_division=0)),
        "f1": float(f1_score(y_true, predicted, zero_division=0)),
        "threshold": 0.5,
    }


def compare_models(frame: pd.DataFrame, artifacts_dir: Path, test_size: float = 0.2, dataset_source: str = "") -> list[dict]:
    if frame["toxic"].nunique() != 2:
        raise ValueError("The dataset must contain both toxic and non-toxic comments.")
    if frame["toxic"].value_counts().min() < 2:
        raise ValueError("Each class requires at least two rows for a stratified split.")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    train, test = train_test_split(frame, test_size=test_size, stratify=frame["toxic"], random_state=RANDOM_STATE)
    results: list[dict] = []
    best_model = None
    best_probabilities = None
    for name, model in build_models().items():
        model.fit(train["comment_text"], train["toxic"])
        probabilities = model.predict_proba(test["comment_text"])[:, 1]
        result = _metrics(test["toxic"], probabilities, name)
        result["test_predictions"] = pd.DataFrame({
            "id": test["id"].astype(str).to_numpy(),
            "actual": test["toxic"].to_numpy(),
            "predicted": (probabilities >= 0.5).astype(int),
            "probability": probabilities,
        })
        results.append(result)
        if best_model is None or (result["roc_auc"], result["f1"]) > max(
            (item["roc_auc"], item["f1"]) for item in results[:-1]
        ):
            best_model, best_probabilities = model, probabilities

    metric_columns = ["model_name", "vectorizer", "roc_auc", "pr_auc", "precision", "recall", "f1", "threshold"]
    pd.DataFrame([{key: result[key] for key in metric_columns} for result in results]).to_csv(artifacts_dir / "comparison.csv", index=False)
    # ROC-AUC is primary; F1 breaks an exact ROC-AUC tie at the stated threshold.
    best = max(results, key=lambda item: (item["roc_auc"], item["f1"]))
    serialisable = {key: best[key] for key in metric_columns}
    serialisable["train_rows"] = int(len(train))
    serialisable["test_rows"] = int(len(test))
    serialisable["random_state"] = RANDOM_STATE
    serialisable["dataset_source"] = dataset_source
    serialisable["is_synthetic_smoke_test"] = Path(dataset_source).name == "sample_train.csv"
    (artifacts_dir / "metrics.json").write_text(json.dumps(serialisable, indent=2), encoding="utf-8")
    joblib.dump(best_model, artifacts_dir / "best_model.joblib")
    _plot_evaluation(test["toxic"].to_numpy(), best_probabilities, best["model_name"], artifacts_dir)
    return results


def _plot_evaluation(y_true: np.ndarray, probabilities: np.ndarray, model_name: str, artifacts_dir: Path) -> None:
    sns.set_theme(style="whitegrid")
    fpr, tpr, _ = roc_curve(y_true, probabilities)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, label=f"{model_name} (AUC = {roc_auc_score(y_true, probabilities):.3f})", color="#1f77b4", linewidth=2)
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Random classifier")
    ax.set(xlabel="False positive rate", ylabel="True positive rate", title="ROC curve")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(artifacts_dir / "roc_curve.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay(confusion_matrix(y_true, (probabilities >= 0.5).astype(int)), display_labels=["Non-toxic", "Toxic"]).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Confusion matrix at threshold 0.50")
    fig.tight_layout()
    fig.savefig(artifacts_dir / "confusion_matrix.png", dpi=180)
    plt.close(fig)


def predict_text(artifacts_dir: Path, text: str) -> tuple[float, int]:
    model_path = artifacts_dir / "best_model.joblib"
    if not model_path.exists():
        raise FileNotFoundError("No saved model. Run the comparison first.")
    probability = float(joblib.load(model_path).predict_proba([text])[:, 1][0])
    return probability, int(probability >= 0.5)

