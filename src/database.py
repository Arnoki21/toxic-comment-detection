from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialise_database(database_path: Path, comments: pd.DataFrame) -> None:
    """Create the SQLite schema and replace the imported comments table."""
    with connect(database_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS comments (
                comment_id TEXT PRIMARY KEY,
                comment_text TEXT NOT NULL,
                toxic INTEGER NOT NULL CHECK(toxic IN (0, 1)),
                severe_toxic INTEGER NOT NULL,
                obscene INTEGER NOT NULL,
                threat INTEGER NOT NULL,
                insult INTEGER NOT NULL,
                identity_hate INTEGER NOT NULL,
                char_length INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS model_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                vectorizer TEXT NOT NULL,
                roc_auc REAL NOT NULL,
                precision REAL NOT NULL,
                recall REAL NOT NULL,
                f1 REAL NOT NULL,
                trained_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                comment_id TEXT NOT NULL,
                actual INTEGER NOT NULL,
                predicted INTEGER NOT NULL,
                probability REAL NOT NULL,
                FOREIGN KEY(run_id) REFERENCES model_runs(run_id),
                FOREIGN KEY(comment_id) REFERENCES comments(comment_id)
            );
            """
        )
        conn.execute("DELETE FROM predictions")
        conn.execute("DELETE FROM model_runs")
        conn.execute("DELETE FROM comments")
        comments.rename(columns={"id": "comment_id"}).to_sql("comments", conn, if_exists="append", index=False)


def save_run(database_path: Path, result: dict, test_rows: pd.DataFrame) -> int:
    timestamp = datetime.now(timezone.utc).isoformat()
    with connect(database_path) as conn:
        cursor = conn.execute(
            """INSERT INTO model_runs (model_name, vectorizer, roc_auc, precision, recall, f1, trained_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (result["model_name"], result["vectorizer"], result["roc_auc"], result["precision"], result["recall"], result["f1"], timestamp),
        )
        run_id = int(cursor.lastrowid)
        conn.executemany(
            """INSERT INTO predictions (run_id, comment_id, actual, predicted, probability)
               VALUES (?, ?, ?, ?, ?)""",
            [
                (run_id, str(row.id), int(row.actual), int(row.predicted), float(row.probability))
                for row in test_rows.itertuples(index=False)
            ],
        )
    return run_id


def run_query(database_path: Path, sql: str) -> pd.DataFrame:
    with connect(database_path) as conn:
        return pd.read_sql_query(sql, conn)

