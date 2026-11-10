from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "toxic_comment_detection_report.docx"
METRICS = ROOT / "artifacts" / "metrics.json"


def shade(cell, fill: str) -> None:
    props = cell._tc.get_or_add_tcPr()
    node = OxmlElement("w:shd")
    node.set(qn("w:fill"), fill)
    props.append(node)


def set_cell_text(cell, text: str, bold: bool = False, color: str = "000000") -> None:
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        shade(cell, "1F4E78")
        set_cell_text(cell, header, bold=True, color="FFFFFF")
    for row in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            if len(table.rows) % 2 == 0:
                shade(cells[index], "EAF2F8")
            set_cell_text(cells[index], value)
    if widths:
        for row in table.rows:
            for cell, width in zip(row.cells, widths):
                cell.width = Inches(width)
    doc.add_paragraph()


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    paragraph = doc.add_heading(text, level=level)
    paragraph.paragraph_format.space_before = Pt(12)
    paragraph.paragraph_format.space_after = Pt(6)


def add_body(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph(text)
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.line_spacing = 1.15


def metric_text(metrics: dict, key: str) -> str:
    if key not in metrics:
        return "Run `python -m src.cli compare --data data/raw/train.csv` and rebuild this report."
    value = metrics[key]
    return f"{value:.4f}" if isinstance(value, float) else str(value)


def main() -> None:
    metrics = json.loads(METRICS.read_text(encoding="utf-8")) if METRICS.exists() else {}
    if metrics.get("is_synthetic_smoke_test"):
        metrics = {}
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)
    styles = doc.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"].font.size = Pt(10.5)
    styles["Title"].font.name = "Aptos Display"
    styles["Title"].font.size = Pt(23)
    styles["Title"].font.color.rgb = RGBColor(0, 0, 0)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("Toxic Comment Detection")
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run("Final Project Report\nApplied Artificial Intelligence").italic = True
    doc.add_paragraph()
    add_table(doc, ["Full name", "Group", "Contribution"], [
        ["Replace with member 1", "Replace with group", "Data preparation, database, exploratory analysis"],
        ["Replace with member 2", "Replace with group", "Model training, evaluation, error analysis"],
        ["Replace with member 3", "Replace with group", "Documentation, presentation, demonstration"],
    ], [1.8, 1.1, 3.6])

    add_heading(doc, "Project summary")
    add_body(doc, "This project classifies English Wikipedia discussion comments as toxic or non-toxic. It uses the Jigsaw Toxic Comment Classification Challenge training data, compares two reproducible scikit-learn models, and records data and experiment outputs in SQLite. The project focuses on class imbalance, ROC-AUC, confusion-matrix interpretation, and qualitative error analysis.")

    add_heading(doc, "Objectives")
    add_body(doc, "The project aims to build a reliable binary classifier for the toxic label, quantify the effect of feature design, evaluate models with metrics suitable for imbalanced data, and provide a simple console interface for analysis and custom predictions.")

    add_heading(doc, "Data")
    add_body(doc, "The source is the Jigsaw Toxic Comment Classification Challenge on Kaggle. The official train.csv file includes comment_text and six toxicity-related labels. The binary target in this project is toxic. Empty comments are removed, whitespace is normalized, and the five remaining labels are retained for database analysis.")
    add_table(doc, ["Field", "Use in this project"], [
        ["id", "Unique comment identifier and database key"],
        ["comment_text", "Model input after minimal whitespace cleaning"],
        ["toxic", "Binary target: 1 toxic, 0 non-toxic"],
        ["severe_toxic, obscene, threat, insult, identity_hate", "Stored for follow-up exploration"],
        ["char_length", "Derived field for descriptive and error analysis"],
    ], [2.2, 4.3])

    add_heading(doc, "Methods")
    add_body(doc, "The dataset is split into training and test partitions with stratification and random_state=42. Stratification preserves the toxic/non-toxic class ratio in both partitions. Both models use Logistic Regression with class_weight='balanced', which gives more influence to the minority toxic class during optimization.")
    add_table(doc, ["Model", "Features", "Purpose"], [
        ["Word TF-IDF Logistic Regression", "Word 1-2 grams, sublinear term frequency", "Transparent baseline for meaningful words and short phrases"],
        ["Word and character TF-IDF Logistic Regression", "Word 1-2 grams plus character-within-word 3-5 grams", "Tests whether spelling variants and character patterns improve detection"],
    ], [2.0, 2.8, 1.7])
    add_body(doc, "ROC-AUC is the primary ranking metric because it assesses probability ranking across thresholds and does not depend on the majority class. Precision, recall, F1, PR-AUC, and a confusion matrix complement ROC-AUC. The standard 0.50 threshold is used for the initial confusion matrix; it can be adjusted after considering moderation costs.")

    add_heading(doc, "Implementation")
    add_body(doc, "The repository uses modular Python files: data.py validates and cleans input; modeling.py builds, trains, evaluates, and saves models; database.py manages SQLite; and cli.py provides the command line and an interactive menu. The menu uses conditionals, a loop, functions, list and dictionary collections, and try/except handling for missing files and invalid commands.")
    add_body(doc, "SQLite stores comments, model runs, and test predictions. The supplied sql_queries.sql contains eight documented queries, including class balance, comment length, model leaderboard, confusion-matrix cells, high-confidence false positives and false negatives, and a ranked model comparison using a CTE and window function.")

    add_heading(doc, "Results")
    if metrics:
        add_body(doc, "The following values were loaded from artifacts/metrics.json after a completed pipeline run on the current dataset. Record the dataset file, execution date, and library versions with the final submission.")
    else:
        add_body(doc, "No official Kaggle run is included in this repository. Run the comparison on data/raw/train.csv, then rebuild this report to insert measured values. Do not replace these fields with metrics from the synthetic smoke-test dataset.")
    add_table(doc, ["Metric", "Current value"], [
        ["Selected model", str(metrics.get("model_name", "Pending official dataset run"))],
        ["ROC-AUC", metric_text(metrics, "roc_auc")],
        ["PR-AUC", metric_text(metrics, "pr_auc")],
        ["Precision at 0.50", metric_text(metrics, "precision")],
        ["Recall at 0.50", metric_text(metrics, "recall")],
        ["F1 at 0.50", metric_text(metrics, "f1")],
        ["Training rows", metric_text(metrics, "train_rows")],
        ["Test rows", metric_text(metrics, "test_rows")],
    ], [2.2, 4.3])
    add_body(doc, "The generated roc_curve.png and confusion_matrix.png provide the final visual evidence. Error-analysis SQL queries should be reviewed before deployment because a false positive can suppress acceptable speech and a false negative can leave harmful content visible.")

    add_heading(doc, "Conclusion")
    add_body(doc, "The project provides a repeatable baseline for toxic-comment detection and makes its evaluation assumptions explicit. The final model should be selected by measured ROC-AUC on the held-out test split, then checked against precision, recall, and representative error cases. A future extension can compare this baseline with a fine-tuned transformer using the same split and metrics.")

    add_heading(doc, "Reproducibility")
    add_body(doc, "Install requirements.txt, download the official Kaggle train.csv to data/raw/train.csv, and run python -m src.cli compare --data data/raw/train.csv. The command writes artifacts/metrics.json, comparison.csv, roc_curve.png, confusion_matrix.png, best_model.joblib, and toxic_comments.db. The requirements file pins core package versions.")

    add_heading(doc, "References")
    add_body(doc, "Jigsaw Toxic Comment Classification Challenge. Kaggle. https://www.kaggle.com/competitions/jigsaw-toxic-comment-classification-challenge")
    add_body(doc, "Pedregosa et al. Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 2011.")
    add_body(doc, "Rajaraman and Ullman. Mining of Massive Datasets. Cambridge University Press, 2011.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
