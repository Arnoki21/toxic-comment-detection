# Toxic Comment Detection

A reproducible final project for binary toxic-comment classification using the Jigsaw Toxic Comment Classification Challenge dataset. The project compares two TF-IDF + Logistic Regression models, handles class imbalance, reports ROC-AUC and a confusion matrix, stores data and predictions in SQLite, and exposes the workflow through a console menu.

## Project Goal

The goal is to classify each Wikipedia discussion comment as **toxic** or **non-toxic**. The project answers four practical questions:

1. How imbalanced is the toxic/non-toxic target?
2. Does adding character n-grams improve a word TF-IDF baseline?
3. Which model produces the strongest held-out ROC-AUC?
4. What false positives and false negatives should a moderator review?

## Team

| Team member | Main responsibility | Concrete deliverables | Share |
| --- | --- | --- |
| **Alikhan Sailybaev, AAI-2601** | Data and database | Validate `train.csv`; analyze missing values and class balance; explain the SQLite schema; interpret SQL queries 1-3 | 33% |
| **Danial Shaimurat, AAI-2601** | Modeling and evaluation | Explain TF-IDF, Logistic Regression, stratified split, class weights, ROC-AUC, precision, recall, F1, ROC curve, and confusion matrix; run model comparison | 33% |
| **Arnur Adilkhan, AAI-2601** | Error analysis and delivery | Review false positives and false negatives; update report results, prepare slides, check reproducibility, and lead the project demonstration | 33% |

All members must understand the full project and be able to run `python -m src.cli`. During the defense, Member 1 presents the data, Member 2 presents models and metrics, and Member 3 presents error analysis and conclusions. Update this table and the same table in the report and presentation before submission.

## Dataset

Download `train.csv` from the [Jigsaw Toxic Comment Classification Challenge](https://www.kaggle.com/competitions/jigsaw-toxic-comment-classification-challenge). Kaggle authentication may be required. Put the file at `data/raw/train.csv`.

The training data contains a `comment_text` column and six label columns. This project uses `toxic` as the binary target required by the selected topic. The other label columns remain available in SQLite for future analysis.

| Column | Description | Project use |
| --- | --- | --- |
| `id` | Unique comment identifier | Database key and prediction join |
| `comment_text` | Original Wikipedia discussion comment | Model input |
| `toxic` | Main binary label | Target: 1 toxic, 0 non-toxic |
| Other five labels | More specific toxicity labels | Stored for further analysis |

## Quick start

Python 3.11 is recommended.

```powershell
cd "C:\Users\Lenovo\OneDrive\Документы\ChatGPT\programmingAI_final"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.cli
```

Using `.\.venv\Scripts\python.exe` avoids PowerShell execution-policy problems and ensures the project uses its own installed packages.

Or run the reproducible command sequence:

```powershell
.\.venv\Scripts\python.exe -m src.cli prepare --data data/raw/train.csv
.\.venv\Scripts\python.exe -m src.cli compare --data data/raw/train.csv
.\.venv\Scripts\python.exe -m src.cli sql --name class_distribution
.\.venv\Scripts\python.exe -m src.cli predict --text "Your custom comment goes here"
```

## What the project does

1. Validates the input file and removes missing comments.
2. Normalizes whitespace and creates a character-length feature for analysis.
3. Creates a stratified 80/20 train/test split with `random_state=42`.
4. Handles class imbalance with `class_weight="balanced"` in Logistic Regression.
5. Compares a word n-gram TF-IDF baseline with a combined word-and-character n-gram model.
6. Selects the model with the best held-out ROC-AUC, using F1 as a tie-breaker.
7. Writes ROC and confusion-matrix figures plus a machine-readable metrics file to `artifacts/`.
8. Saves comments, experiment runs, predictions, and error cases in SQLite.
9. Provides eight documented SQL queries in `sql_queries.sql`.

## Models and Evaluation

| Model | Features | Purpose |
| --- | --- | --- |
| `word_tfidf_lr` | Word TF-IDF, 1-2 grams | Clear, interpretable baseline for words and short phrases |
| `word_char_tfidf_lr` | Word TF-IDF, 1-2 grams; character-within-word TF-IDF, 3-5 grams | Captures spelling variation and obfuscated toxic terms |

Accuracy can be misleading for an imbalanced target, so the project reports ROC-AUC, PR-AUC, precision, recall, F1, and a confusion matrix at threshold 0.50. The generated false-positive and false-negative SQL queries support honest error analysis. The pipeline also produces class-balance, comment-length, and common n-gram EDA figures.

## Expected outputs

After `compare`, the `artifacts/` directory contains `metrics.json`, `comparison.csv`, `roc_curve.png`, `confusion_matrix.png`, and `best_model.joblib`. Results depend on the exact data split and library versions, so the report and slides deliberately contain fields to fill from the generated metrics instead of invented scores.

| Output | Purpose |
| --- | --- |
| `comparison.csv` | Metrics for both compared models |
| `metrics.json` | Selected-model metrics, row counts, random seed, and data-source metadata |
| `roc_curve.png` | ROC curve for the selected model |
| `confusion_matrix.png` | Classification outcomes at the 0.50 threshold |
| `best_model.joblib` | Model used by the custom-prediction command |
| `toxic_comments.db` | SQLite comments, runs, and predictions tables |

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
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.cli compare --data data/sample_train.csv --test-size 0.25
```

The sample file only verifies that the pipeline works. Do not use its metrics in the final report or presentation.

## SQL Queries

The SQLite database has three related tables: `comments`, `model_runs`, and `predictions`. The eight queries in `sql_queries.sql` cover class balance, length statistics, longest comments, a model leaderboard, confusion-matrix cells, high-confidence false positives, high-confidence false negatives, and a CTE/window-function ranking.

For example:

```powershell
.\.venv\Scripts\python.exe -m src.cli sql --name ranking
```

Available names: `class_distribution`, `average_length`, `longest_comments`, `leaderboard`, `confusion_cells`, `false_positives`, `false_negatives`, and `ranking`.

## Final Submission Checklist

- [ ] Replace the three team-member placeholders here, in the report, and in the presentation.
- [ ] Download the official Kaggle `train.csv` file.
- [ ] Run `compare` on the official dataset.
- [ ] Add the generated official metrics and figures to the report and slides.
- [ ] Discuss representative false positives and false negatives.
- [ ] Demonstrate the console menu and a custom prediction.
- [ ] Push the final version to GitHub.

## Optional Transformer extension

The required, fully runnable pipeline uses scikit-learn. A team may add a fine-tuning experiment with `distilbert-base-uncased` after the baseline is complete. Report its data split, random seed, training device, epochs, and ROC-AUC beside the baseline so the comparison remains fair.

