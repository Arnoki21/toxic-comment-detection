from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS


def generate_eda(frame: pd.DataFrame, artifacts_dir: Path) -> None:
    """Create reproducible text and class-distribution figures for the report."""
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    _class_distribution(frame, artifacts_dir)
    _length_distribution(frame, artifacts_dir)
    _top_ngrams(frame, artifacts_dir)


def _class_distribution(frame: pd.DataFrame, artifacts_dir: Path) -> None:
    labels = frame["toxic"].map({0: "Non-toxic", 1: "Toxic"})
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.countplot(x=labels, order=["Non-toxic", "Toxic"], hue=labels, palette=["#6BAED6", "#D95F5F"], legend=False, ax=ax)
    ax.set(title="Class distribution", xlabel="Label", ylabel="Number of comments")
    for container in ax.containers:
        ax.bar_label(container, fmt="%d", padding=3)
    fig.tight_layout()
    fig.savefig(artifacts_dir / "class_distribution.png", dpi=180)
    plt.close(fig)


def _length_distribution(frame: pd.DataFrame, artifacts_dir: Path) -> None:
    sampled = pd.concat(
        [group.sample(n=min(len(group), 20_000), random_state=42) for _, group in frame.groupby("toxic")],
        ignore_index=True,
    )
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    sns.histplot(data=sampled, x="char_length", hue="toxic", bins=60, element="step", stat="density", common_norm=False, palette={0: "#6BAED6", 1: "#D95F5F"}, ax=ax)
    ax.set(xlim=(0, 1_500), title="Comment length distribution", xlabel="Characters per comment", ylabel="Density")
    ax.legend(title="Label", labels=["Toxic", "Non-toxic"])
    fig.tight_layout()
    fig.savefig(artifacts_dir / "comment_length_distribution.png", dpi=180)
    plt.close(fig)


def _top_ngrams(frame: pd.DataFrame, artifacts_dir: Path) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
    for axis, label, color, title in zip(
        axes, [0, 1], ["#6BAED6", "#D95F5F"], ["Most common non-toxic n-grams", "Most common toxic n-grams"],
    ):
        text = frame.loc[frame["toxic"] == label, "comment_text"]
        min_df = 1 if len(text) < 100 else 5
        vectorizer = CountVectorizer(stop_words=list(ENGLISH_STOP_WORDS), ngram_range=(1, 2), min_df=min_df, max_features=50_000)
        matrix = vectorizer.fit_transform(text)
        terms = pd.Series(matrix.sum(axis=0).A1, index=vectorizer.get_feature_names_out()).nlargest(12).sort_values()
        axis.barh(terms.index, terms.values, color=color)
        axis.set(title=title, xlabel="Frequency", ylabel="")
    figure.savefig(artifacts_dir / "top_ngrams.png", dpi=180)
    plt.close(figure)
