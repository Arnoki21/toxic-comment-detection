# Toxic Comment Detection

A reproducible final project for binary toxic-comment classification using the Jigsaw Toxic Comment Classification Challenge dataset. The project compares two TF-IDF + Logistic Regression models, handles class imbalance, reports ROC-AUC and a confusion matrix, stores data and predictions in SQLite, and exposes the workflow through a console menu.

## Team

| Full name | Group | Contribution |
| --- | --- | --- |
| Replace with member 1 | Replace with group | Data preparation, SQLite database, exploratory analysis |
| Replace with member 2 | Replace with group | Model training, evaluation, error analysis |
| Replace with member 3 | Replace with group | Documentation, presentation, demo |

Update this table and the same table in the report and presentation before submission.

## Dataset

Download `train.csv` from the [Jigsaw Toxic Comment Classification Challenge](https://www.kaggle.com/competitions/jigsaw-toxic-comment-classification-challenge). Kaggle authentication may be required. Put the file at `data/raw/train.csv`.

The training data contains a `comment_text` column and six label columns. This project uses `toxic` as the binary target required by the selected topic. The other label columns remain available in SQLite for future analysis.

## Quick start

Python 3.11 is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.cli
```

Or run the reproducible command sequence:

```powershell
python -m src.cli prepare --data data/raw/train.csv
python -m src.cli compare --data data/raw/train.csv
python -m src.cli sql --name class_distribution
python -m src.cli predict --text "Your custom comment goes here"
```

## What the project does

1. Validates the input file and removes missing comments.
2. Creates a stratified train/test split and records class imbalance.
3. Compares a word n-gram TF-IDF baseline with a combined word-and-character n-gram model.
4. Selects the model with the best validation ROC-AUC.
5. Writes ROC and confusion-matrix figures plus a machine-readable metrics file to `artifacts/`.
6. Saves comments, experiment runs, predictions, and error cases in SQLite.
7. Provides eight documented SQL queries in `sql_queries.sql`.

## Expected outputs

After `compare`, the `artifacts/` directory contains `metrics.json`, `comparison.csv`, `roc_curve.png`, `confusion_matrix.png`, and `best_model.joblib`. Results depend on the exact data split and library versions, so the report and slides deliberately contain fields to fill from the generated metrics instead of invented scores.

## Project structure

```text
src/                 Python modules and the console menu
data/raw/            Kaggle train.csv goes here (ignored by Git)
data/sample_train.csv Small synthetic smoke-test data, not for final metrics
artifacts/           Generated models, figures, and metrics (ignored by Git)
sql_queries.sql      Eight SQLite analysis queries
report/              Written report template
presentation/        Final presentation template
tests/               Smoke tests
```

## Testing without Kaggle data

```powershell
pytest -q
python -m src.cli compare --data data/sample_train.csv --test-size 0.25
```

The sample file only verifies that the pipeline works. Do not use its metrics in the final report or presentation.

## Optional Transformer extension

The required, fully runnable pipeline uses scikit-learn. A team may add a fine-tuning experiment with `distilbert-base-uncased` after the baseline is complete. Report its data split, random seed, training device, epochs, and ROC-AUC beside the baseline so the comparison remains fair.

