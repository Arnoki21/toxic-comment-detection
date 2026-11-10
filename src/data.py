from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {"id", "comment_text", "toxic"}
OPTIONAL_LABELS = ["severe_toxic", "obscene", "threat", "insult", "identity_hate"]


def load_comments(path: str) -> pd.DataFrame:
    """Read, validate, and minimally clean a Jigsaw-compatible CSV file."""
    try:
        frame = pd.read_csv(path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Dataset not found: {path}. Download train.csv from Kaggle and place it in data/raw/."
        ) from exc
    except UnicodeDecodeError as exc:
        raise ValueError("The dataset must be UTF-8 CSV text.") from exc

    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    cleaned = frame.copy()
    cleaned["comment_text"] = cleaned["comment_text"].fillna("").astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    cleaned = cleaned.loc[cleaned["comment_text"].ne("")].copy()
    cleaned["toxic"] = pd.to_numeric(cleaned["toxic"], errors="coerce").fillna(0).astype(int).clip(0, 1)
    for label in OPTIONAL_LABELS:
        if label not in cleaned:
            cleaned[label] = 0
        cleaned[label] = pd.to_numeric(cleaned[label], errors="coerce").fillna(0).astype(int).clip(0, 1)
    cleaned["char_length"] = cleaned["comment_text"].str.len()
    return cleaned[["id", "comment_text", "toxic", *OPTIONAL_LABELS, "char_length"]]


def dataset_summary(frame: pd.DataFrame) -> dict[str, float | int]:
    counts = frame["toxic"].value_counts().to_dict()
    total = len(frame)
    toxic_count = int(counts.get(1, 0))
    return {
        "rows": total,
        "toxic_comments": toxic_count,
        "non_toxic_comments": int(counts.get(0, 0)),
        "toxic_rate": round(toxic_count / total, 6) if total else 0.0,
        "average_characters": round(float(frame["char_length"].mean()), 2) if total else 0.0,
    }

