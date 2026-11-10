from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import ARTIFACTS_DIR, DATABASE_PATH
from .data import dataset_summary, load_comments
from .database import initialise_database, run_query, save_run
from .modeling import compare_models, predict_text


def prepare(data_path: str) -> None:
    frame = load_comments(data_path)
    initialise_database(DATABASE_PATH, frame)
    print(json.dumps(dataset_summary(frame), indent=2))
    print(f"SQLite database created: {DATABASE_PATH}")


def compare(data_path: str, test_size: float) -> None:
    frame = load_comments(data_path)
    initialise_database(DATABASE_PATH, frame)
    results = compare_models(frame, ARTIFACTS_DIR, test_size, data_path)
    for result in results:
        run_id = save_run(DATABASE_PATH, result, result["test_predictions"])
        print(f"{result['model_name']}: ROC-AUC={result['roc_auc']:.4f}, F1={result['f1']:.4f}, run_id={run_id}")
    print(f"Saved outputs in {ARTIFACTS_DIR}")


def sql(name: str) -> None:
    queries = Path(__file__).resolve().parents[1] / "sql_queries.sql"
    blocks = [block.strip() for block in queries.read_text(encoding="utf-8").split(";") if block.strip()]
    named = {
        "class_distribution": blocks[0], "average_length": blocks[1], "longest_comments": blocks[2],
        "leaderboard": blocks[3], "confusion_cells": blocks[4], "false_positives": blocks[5],
        "false_negatives": blocks[6], "ranking": blocks[7],
    }
    if name not in named:
        raise ValueError(f"Unknown query '{name}'. Choose: {', '.join(named)}")
    print(run_query(DATABASE_PATH, named[name]).to_string(index=False))


def menu(default_data: str) -> None:
    options = {
        "1": "Check dataset and import it into SQLite",
        "2": "Train and compare models",
        "3": "Run class-balance SQL query",
        "4": "Run model leaderboard SQL query",
        "5": "Classify a custom comment",
        "0": "Exit",
    }
    while True:
        print("\nToxic Comment Detection")
        for key, label in options.items():
            print(f"{key}. {label}")
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                prepare(default_data)
            elif choice == "2":
                compare(default_data, 0.2)
            elif choice == "3":
                sql("class_distribution")
            elif choice == "4":
                sql("leaderboard")
            elif choice == "5":
                text = input("Comment: ").strip()
                probability, label = predict_text(ARTIFACTS_DIR, text)
                print(f"Toxic probability: {probability:.3f}; prediction: {'toxic' if label else 'non-toxic'}")
            elif choice == "0":
                return
            else:
                print("Choose a listed menu option.")
        except (FileNotFoundError, ValueError) as exc:
            print(f"Cannot complete the action: {exc}")


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description="Toxic Comment Detection final project")
    sub = command.add_subparsers(dest="command")
    for name in ("prepare", "compare"):
        item = sub.add_parser(name)
        item.add_argument("--data", default="data/raw/train.csv")
        if name == "compare":
            item.add_argument("--test-size", type=float, default=0.2)
    item = sub.add_parser("sql")
    item.add_argument("--name", required=True)
    item = sub.add_parser("predict")
    item.add_argument("--text", required=True)
    sub.add_parser("menu")
    return command


def main() -> None:
    args = parser().parse_args()
    if args.command == "prepare":
        prepare(args.data)
    elif args.command == "compare":
        compare(args.data, args.test_size)
    elif args.command == "sql":
        sql(args.name)
    elif args.command == "predict":
        probability, label = predict_text(ARTIFACTS_DIR, args.text)
        print(json.dumps({"toxic_probability": round(probability, 6), "prediction": "toxic" if label else "non-toxic"}))
    else:
        menu("data/raw/train.csv")


if __name__ == "__main__":
    main()

